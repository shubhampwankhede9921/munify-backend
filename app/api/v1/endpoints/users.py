from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserResponse, UserListResponse, UserAndPartyResponse, UserWithParty, ExternalUserRegistration
from app.models.user import User as UserModel
from app.models.party import Party as PartyModel
from passlib.context import CryptContext
from app.core.config import settings
from app.services.user_service import register_user_with_optional_roles, get_users_from_perdix, get_user_from_perdix_by_login, update_user_in_perdix
from fastapi.responses import JSONResponse

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all users with pagination and associated party data"""
    query = db.query(UserModel).options(joinedload(UserModel.party))
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return {"status": "success", "message": "Users fetched successfully", "data": users, "total": total}

@router.get("/perdix", status_code=status.HTTP_200_OK)
def get_perdix_users(
    branch_name: Optional[str] = Query(None, description="Filter users by branch name"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    """Get users list from Perdix API with pagination and optional branch filter"""
    body, status_code, is_json = get_users_from_perdix(branch_name=branch_name, page=page, per_page=per_page)
    
    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=body if isinstance(body, str) else body.get("message", "Failed to fetch users from Perdix")
        )
    
    return {
        "status": "success",
        "message": "Users fetched from Perdix successfully",
        "data": body if is_json else {"raw": body}
    }

@router.get("/perdix/{login}", status_code=status.HTTP_200_OK)
def get_perdix_user_by_login(login: str):
    """Get single user details from Perdix by login/username"""
    body, status_code, is_json = get_user_from_perdix_by_login(login)

    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=body if isinstance(body, str) else body.get("message", "Failed to fetch user from Perdix")
        )

    return {
        "status": "success",
        "message": "User fetched from Perdix successfully",
        "data": body if is_json else {"raw": body}
    }

@router.get("/perdix/userid/{userid}", status_code=status.HTTP_200_OK)
def get_perdix_user_by_userid(userid: str):
    """Alias: Get Perdix user by userId (mapped to login)"""
    body, status_code, is_json = get_user_from_perdix_by_login(userid)

    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=body if isinstance(body, str) else body.get("message", "Failed to fetch user from Perdix")
        )

    return {
        "status": "success",
        "message": "User fetched from Perdix successfully",
        "data": body if is_json else {"raw": body}
    }

@router.put("/perdix", status_code=status.HTTP_200_OK)
def update_perdix_user(payload: dict):
    """Forward user update to Perdix (PUT /api/users)"""
    body, status_code, is_json = update_user_in_perdix(payload)
    return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)

@router.get("/{user_id}", response_model=UserAndPartyResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID with associated party data"""
    # Method 1: Use joinedload to eagerly load the party relationship (Recommended)
    user = db.query(UserModel).options(joinedload(UserModel.party)).filter(UserModel.id == user_id).first()
    
    # Method 2: Alternative - Manual join query (if you need more control)
    # user = db.query(UserModel, PartyModel).join(PartyModel, UserModel.party_id == PartyModel.id).filter(UserModel.id == user_id).first()
    
    # Method 3: Two separate queries (if you want to handle the case where party might be null)
    # user = db.query(UserModel).filter(UserModel.id == user_id).first()
    # if user and user.party_id:
    #     party = db.query(PartyModel).filter(PartyModel.id == user.party_id).first()
    #     user.party = party
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"status": "success", "message": "User fetched successfully", "data": user}

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Validate party if provided
    if user.party_id is not None:
        party = db.query(PartyModel).filter(PartyModel.id == user.party_id).first()
        if not party:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="party_id does not reference an existing Party"
            )

    # Hash password
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data.pop("password")
    user_data["password_hash"] = hashed_password
    
    db_user = UserModel(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"status": "success", "message": "User created successfully", "data": db_user}

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return {"status": "success", "message": "User updated successfully", "data": db_user}

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return {"status": "success", "message": "User deleted successfully"}


@router.post("/register")
def register_external_user(payload: ExternalUserRegistration):
    required_payload = {
        "roleCode": "A",
        "activated": True,
        "userState": "ACTIVE",
        "userType": "A",
        "bankName": "Witfin",
        "validUntil": "2035-09-22",
        "accessType": "BRANCH",
        "imeiNumber": "",
        "langKey": "en",
        "userRoles": [],
        "userBranches": [],
        "userName": payload.full_name,
        "login": payload.login,
        "password": payload.password,
        "confirmPassword": payload.confirm_password,
        "email": str(payload.email),
        "mobileNumber": payload.mobile_number,
        "branchId": 12,
        "branchName": "Head Office",
        "changePasswordOnLogin": True,
    }

    body, status_code, is_json = register_user_with_optional_roles(payload)
    return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
