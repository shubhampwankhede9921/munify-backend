from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    author_name: str
    author_email: EmailStr

class CommentCreate(CommentBase):
    post_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None

class CommentInDB(CommentBase):
    id: int
    post_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Comment(CommentInDB):
    pass


class CommentResponse(BaseModel):
    status: str
    message: str
    data: Comment

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    status: str
    message: str
    data: List[Comment]
    total: int

    class Config:
        from_attributes = True
