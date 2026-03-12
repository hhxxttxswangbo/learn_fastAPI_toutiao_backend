from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud.favorite import is_news_favorite, add_favorite_news, delete_favorite_news
from crud.users import update_user, update_user_password
from models.users import User
from schemas.favorite import FavoriteCheckResponse, AddFavoriteRequest
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, userUpdateRequest, passwordUpdateRequest
from config.db_conf import get_db
from crud import users
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


# 获取收藏状态
@router.get("/check")
async def check(news_id: int = Query(..., alias="newsId"), user: User = Depends(get_current_user),
                db: AsyncSession = Depends(get_db)):
    is_favorite = await is_news_favorite(db, user.id, news_id)
    # 要构造包含is_favorite的对象
    return success_response(message="获取收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorite))


# 添加收藏
@router.post("/add")
async def add_favorite(news_data: AddFavoriteRequest, user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    result = await add_favorite_news(db, user.id, news_data.news_id)
    return success_response(message="收藏成功", data=result)


# 取消收藏
@router.delete("/remove")
async def delete_favorite(news_id: int = Query(..., alias="newsId"), user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    result = await delete_favorite_news(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏记录不存在")
    return success_response(message="取消收藏成功", data=result)
