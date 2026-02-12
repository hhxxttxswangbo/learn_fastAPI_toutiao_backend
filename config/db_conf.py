"""
数据库配置模块

这个文件负责配置数据库连接，包括：
1. 定义数据库连接 URL
2. 创建异步数据库引擎（Engine）
3. 创建异步会话工厂（Session Maker）
4. 定义获取数据库会话的依赖项函数

使用异步数据库操作可以提高并发性能，特别是在高并发场景下。
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库连接 URL
# 格式：mysql+aiomysql://用户名:密码@主机:端口/数据库名?参数
# aiomysql 是 MySQL 的异步驱动
ASYNC_DATABASE_URL = "mysql+aiomysql://root:hhxxttxsWANGBO07@localhost:3306/news_app?charset=utf8mb4"


# 创建异步数据库引擎
# Engine 是数据库连接的核心对象，负责管理数据库连接池
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,  # 数据库连接 URL
    echo=True,  # 输出 SQL 日志：True 表示在控制台打印执行的 SQL 语句（开发调试时很有用，生产环境建议设为 False）
    pool_size=10,  # 连接池大小：设置连接池中保持的持久连接数（最小连接数）
    max_overflow=20  # 最大溢出连接数：当连接池中的连接用完时，允许额外创建的连接数
)


# 创建异步会话工厂
# Session Maker 是一个工厂函数，用于创建数据库会话（Session）
# 会话是与数据库交互的主要方式，负责执行 SQL 语句和管理事务
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  # 绑定到上面创建的数据库引擎
    class_=AsyncSession,  # 使用异步会话类
    expire_on_commit=False  # 提交后不过期对象：False 表示提交后对象仍然有效，可以继续访问其属性
)


# 定义获取数据库会话的依赖项函数
# 这个函数配合 FastAPI 的 Depends 使用，用于在路由处理函数中自动获取数据库会话
# 使用依赖注入可以确保会话的正确管理（打开、提交、回滚、关闭）
async def get_db():
    """
    获取数据库会话的依赖项函数
    
    Yields:
        AsyncSession: 数据库会话对象，用于执行数据库操作
        
    使用方式：
        @router.get("/categories")
        async def get_categories(db: AsyncSession = Depends(get_db)):
            # 使用 db 会话进行数据库操作
            pass
            
    工作流程：
        1. 创建新的数据库会话
        2. 将会话 yield 给路由处理函数使用
        3. 如果执行成功，提交事务
        4. 如果发生异常，回滚事务
        5. 无论成功或失败，最终都会关闭会话
    """
    async with AsyncSessionLocal() as session:
        try:
            # 将会话 yield 出去，供路由处理函数使用
            yield session
            # 如果路由处理函数执行成功，提交事务（保存更改到数据库）
            await session.commit()
        except Exception:
            # 如果路由处理函数执行过程中发生异常，回滚事务（撤销所有未提交的更改）
            await session.rollback()
            # 重新抛出异常，让上层处理
            raise
        finally:
            # 无论成功或失败，都关闭数据库会话，释放连接回连接池
            await session.close()