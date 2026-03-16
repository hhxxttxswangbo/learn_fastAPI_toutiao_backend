# 根据token查询用户并返回用户
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from crud import users

# 创建 HTTPBearer 安全方案实例
# 这会让 Swagger 文档显示 "Authorize" 按钮
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    从请求头获取 token 并验证用户
    
    使用 HTTPBearer 安全方案，Swagger 文档会自动显示认证按钮
    前端请求时需要在 Header 中携带: Authorization: Bearer <token>
    """
    token = credentials.credentials
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌过期或无效")
    return user
