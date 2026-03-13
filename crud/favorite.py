import uuid
from datetime import datetime, timedelta

from charset_normalizer import detect
from fastapi import HTTPException
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from models.news import News


# 检查当前账号当前新闻是否收藏
async def is_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)

    return result.scalar_one_or_none() is not None


async def add_favorite_news(db: AsyncSession, user_id: int, news_id: int):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def delete_favorite_news(db: AsyncSession, user_id: int, news_id: int):
    query = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    # 总量
    count_query = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()  # 只能有一个

    # 查询收藏的新闻列表，需要有新闻信息  联表查询 join() 收藏时间排序 分页
    # select(查询主体模型类).join(联合查询的模型类, 联合查询的条件)
    # News表和Favorite表里都有created_at和id，不知道以哪个为准，因此需要取别名
    # 别名：Favorite.created_at.label('favorite_time')
    offset = (page - 1) * page_size
    # [
    #   (新闻对象，收藏时间，收藏id)
    # ]
    query = (select(News, Favorite.created_at.label('favorite_time'), Favorite.id.label('favorite_id'))
             .join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id)
             .order_by(Favorite.created_at.desc())
             .offset(offset).limit(page_size))

    result = await db.execute(query)
    # - 查询单个模型（如 select(News)）→ 用 scalars().all()
    # - 查询多个字段/混合查询 → 用 result.all() 返回完整元组
    rows = result.all()
    return rows, total


async def clear_favorite_news(db: AsyncSession, user_id: int):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0
