from starlette import status
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from crud.history import add_history_news, delete_history_news, get_history_list, clear_history_news
from models.users import User
from config.db_conf import get_db
from schemas.history import AddHistoryRequest, HistoryListResponse
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])


# 添加浏览记录
@router.post("/add")
async def add_history(news_data: AddHistoryRequest, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    result = await add_history_news(db, user.id, news_data.news_id)
    return success_response(message="记录成功", data=result)


# 删除浏览记录
@router.delete("/delete/{news_id}")
async def delete_history(news_id: int, user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    result = await delete_history_news(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="浏览记录不存在")
    return success_response(message="删除浏览记录成功", data=result)


# 获取历史记录列表
@router.get("/list")
async def list_history(user: User = Depends(get_current_user), page: int = Query(1, ge=1),
                       page_size: int = Query(10, alias="pageSize", ge=1, le=100),
                       db: AsyncSession = Depends(get_db)):
    rows, total = await get_history_list(db, user.id, page, page_size)
    # has_more 跳过的 + 当前列表里面的数量 < 总量
    history_list = [{
        **news.__dict__,
        "view_time": view_time,
        "history_id": history_id
    } for news, view_time, history_id in rows]

    has_more = total > page * page_size

    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message='获取历史记录列表成功', data=data)


# 清空收藏列表
@router.delete("/clear")
async def clear_history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    count = await clear_history_news(db, user.id)
    return success_response(message=f"清空收藏了{count}条记录")
