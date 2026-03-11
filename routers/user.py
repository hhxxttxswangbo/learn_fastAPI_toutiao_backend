from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud.users import update_user
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, userUpdateRequest
from config.db_conf import get_db
from crud import users
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post('/register')
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 验证用户是否存在 创建 生成token 响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    user = await users.create_user(db, user_data)

    token = await users.create_token(db, user.id)
    # return {
    #     "code": 200,
    #     "message": "User created successfully",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar,
    #         }
    #
    #     },
    # }

    # model_validate 提取ORM对象User中的属性值
    resource_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="User created successfully", data=resource_data)


@router.post('/login')
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑: 验证用户是否存在  验证密码   生成Token   响应结果

    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    token = await users.create_token(db, user.id)
    resource_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="User logged in", data=resource_data)


# 获取用户信息
@router.get('/info')
# 依赖注入 能拿到get_current_user参数与返回值
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


# 修改用户信息:验证token  更新（用户输入数据 put提交 请求体参数 定义pydantic模型类） 响应结果
@router.put('/update')
# 参数：用户输入的 验证token的 db
async def update_user_info(user_data: userUpdateRequest, user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    user = await update_user(db, user.username, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))
