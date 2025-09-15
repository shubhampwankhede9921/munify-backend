from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.post import Post, PostCreate, PostUpdate, PostResponse, PostListResponse
from app.models.post import Post as PostModel
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=PostListResponse, status_code=status.HTTP_200_OK)
def get_posts(
    skip: int = 0,
    limit: int = 100,
    status: str = "published",
    db: Session = Depends(get_db)
):
    """Get all posts with pagination and status filter"""
    query = db.query(PostModel).filter(PostModel.status == status)
    total = query.count()
    posts = query.offset(skip).limit(limit).all()
    return {"status": "success", "message": "Posts fetched successfully", "data": posts, "total": total}

@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return {"status": "success", "message": "Post fetched successfully", "data": post}

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    # Check if author exists
    author = db.query(User).filter(User.id == post.author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    db_post = PostModel(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"status": "success", "message": "Post created successfully", "data": db_post}

@router.put("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    """Update a post"""
    db_post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    update_data = post.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    return {"status": "success", "message": "Post updated successfully", "data": db_post}

@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    return {"status": "success", "message": "Post deleted successfully"}

@router.get("/shubham", status_code=status.HTTP_200_OK)
def get_shubham(db: Session = Depends(get_db)):
    shubham = db.query(User).filter(User.username == "shubham").first()
    if not shubham:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shubham not found"
        )
    return {"status": "success", "message": "Shubham fetched successfully"}