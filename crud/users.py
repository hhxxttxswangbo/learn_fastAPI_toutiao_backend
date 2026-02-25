from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models.users import User


# 根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):
    select(User).where(User.username == username)
