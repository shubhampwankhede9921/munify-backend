from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.comment import Comment, CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from app.models.comment import Comment as CommentModel
from app.models.post import Post

router = APIRouter()

@router.get("/", response_model=CommentListResponse, status_code=status.HTTP_200_OK)
def get_comments(
    skip: int = 0,
    limit: int = 100,
    status: str = "approved",
    db: Session = Depends(get_db)
):
    """Get all comments with pagination and status filter"""
    query = db.query(CommentModel).filter(CommentModel.status == status)
    total = query.count()
    comments = query.offset(skip).limit(limit).all()
    return {"status": "success", "message": "Comments fetched successfully", "data": comments, "total": total}

@router.get("/post/{post_id}", response_model=CommentListResponse, status_code=status.HTTP_200_OK)
def get_comments_by_post(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    status: str = "approved",
    db: Session = Depends(get_db)
):
    """Get all comments for a specific post"""
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    query = db.query(CommentModel).filter(
        CommentModel.post_id == post_id,
        CommentModel.status == status
    )
    total = query.count()
    comments = query.offset(skip).limit(limit).all()
    return {"status": "success", "message": "Comments fetched successfully", "data": comments, "total": total}

@router.get("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a specific comment by ID"""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return {"status": "success", "message": "Comment fetched successfully", "data": comment}

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """Create a new comment"""
    # Check if post exists
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db_comment = CommentModel(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return {"status": "success", "message": "Comment created successfully", "data": db_comment}

@router.put("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db)):
    """Update a comment (mainly for status changes)"""
    db_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    update_data = comment.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_comment, field, value)
    
    db.commit()
    db.refresh(db_comment)
    return {"status": "success", "message": "Comment updated successfully", "data": db_comment}

@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """Delete a comment"""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    db.delete(comment)
    db.commit()
    return {"status": "success", "message": "Comment deleted successfully"}
