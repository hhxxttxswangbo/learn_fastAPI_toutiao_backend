import uuid
from datetime import datetime, timedelta

from charset_normalizer import detect
from fastapi import HTTPException
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import favorite
from models.favorite import Favorite


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
