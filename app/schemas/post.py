from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    slug: Optional[str] = None
    status: str = "draft"

class PostCreate(PostBase):
    author_id: int

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None

class PostInDB(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Post(PostInDB):
    pass


class PostResponse(BaseModel):
    status: str
    message: str
    data: Post

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    status: str
    message: str
    data: List[Post]
    total: int

    class Config:
        from_attributes = True
