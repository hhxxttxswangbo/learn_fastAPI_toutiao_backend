# 根据token查询用户并返回用户
from fastapi import Depends, HTTPException, Header
from starlette import status

from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from crud import users


async def get_current_user(authorization: str = Header(..., alias="authorization"), db: AsyncSession = Depends(get_db)):
    token = authorization.replace('Bearer', '').strip()
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌过期或无效")
    return user
