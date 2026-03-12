from passlib.context import CryptContext
from passlib.exc import UnknownHashError

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 密码加密
def get_password_hash(password: str):
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)


# 密码验证
def verify_password(plain_password, hashed_password):
    try:
        truncated_password = plain_password[:72]
        return pwd_context.verify(truncated_password, hashed_password)
    except (ValueError, UnknownHashError):
        return False
