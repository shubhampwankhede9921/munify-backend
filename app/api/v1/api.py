from fastapi import APIRouter
from app.api.v1.endpoints import posts, users, comments

api_router = APIRouter()

api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
