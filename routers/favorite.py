from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud.favorite import is_news_favorite, add_favorite_news, delete_favorite_news, clear_favorite_news
from crud.users import update_user, update_user_password
from models.users import User
from schemas.favorite import FavoriteCheckResponse, AddFavoriteRequest, FavoriteListResponse
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, userUpdateRequest, passwordUpdateRequest
from config.db_conf import get_db
from crud import users, favorite
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


# 获取收藏列表
@router.get("/list")
async def list_favorites(user: User = Depends(get_current_user), page: int = Query(1, ge=1),
                         page_size: int = Query(10, alias="pageSize", ge=1, le=100),
                         db: AsyncSession = Depends(get_db)):
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    # has_more 跳过的 + 当前列表里面的数量 < 总量
    favorite_list = [{
        **news.__dict__,
        "favorite_time": favorite_time,
        "favorite_id": favorite_id
    } for news, favorite_time, favorite_id in rows]

    has_more = total > page * page_size

    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(message='获取收藏列表成功', data=data)


# 清空收藏列表
@router.delete("/clear")
async def clear_favorites(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    count = await clear_favorite_news(db, user.id)
    return success_response(message=f"清空收藏了{count}条记录")
