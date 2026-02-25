from starlette import status
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest
from config.db_conf import get_db
from crud import users

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post('/register')
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 验证用户是否存在 创建 生成token 响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    user = await users.create_user(db, user_data)

    token = await users.create_token(db, user.id)
    return {
        "code": 200,
        "message": "User created successfully",
        "data": {
            "token": token,
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "bio": user.bio,
                "avatar": user.avatar,
            }

        },
    }
