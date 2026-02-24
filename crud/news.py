"""
新闻相关的数据库操作（CRUD）模块

CRUD 是 Create（创建）、Read（读取）、Update（更新）、Delete（删除）的缩写
这个文件封装了对数据库的操作，将 SQL 逻辑与业务逻辑分离

为什么使用 CRUD 层：
1. 代码复用：多个路由可以调用相同的数据库操作
2. 代码组织：将数据库操作集中管理，便于维护
3. 解耦：路由层只需要调用函数，不需要关心具体的 SQL 实现
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models.news import Category, News


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    获取新闻分类列表（分页查询）
    
    这个函数从数据库中查询新闻分类，支持分页功能
    
    Args:
        db (AsyncSession): 数据库会话对象，由 FastAPI 的依赖注入自动提供
        skip (int, optional): 跳过的记录数（用于分页），默认为 0
                            例如：skip=10 表示跳过前 10 条记录，从第 11 条开始
        limit (int, optional): 返回的最大记录数（每页数量），默认为 100
                             例如：limit=10 表示最多返回 10 条记录
    
    Returns:
        list[Category]: 分类对象的列表，每个对象代表一条分类记录
    
    使用示例：
        # 获取前 10 条分类
        categories = await get_categories(db, skip=0, limit=10)
        
        # 获取第 11-20 条分类（第二页）
        categories = await get_categories(db, skip=10, limit=10)
    
    工作流程：
        1. 构建 SELECT 查询语句
        2. 使用数据库会话执行查询
        3. 从结果中提取并返回所有记录
    """
    # 构建查询语句（Statement）
    # select(Category) 表示要查询 Category 表
    # .offset(skip) 表示跳过前 skip 条记录（分页偏移）
    # .limit(limit) 表示最多返回 limit 条记录（分页大小）
    stmt = select(Category).offset(skip).limit(limit)

    # 执行查询
    # db.execute(stmt) 将查询语句发送到数据库执行
    # await 关键字表示这是一个异步操作，需要等待数据库响应
    result = await db.execute(stmt)

    # 提取结果并返回
    # result.scalars() 提取结果中的标量值（即 Category 对象）
    # .all() 获取所有结果，返回一个列表
    # 返回格式：[Category(...), Category(...), ...]
    return result.scalars().all()


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    # id条件查询   where
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_count(db: AsyncSession, category_id: int):
    # News.id为唯一标识 进行计算查询func.count(News.id)
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 增加浏览量
async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    # 更新立即提交到数据库
    await db.commit()

    # 更新操作时要检查数据库是否真的命中了数据
    return result.rowcount > 0


# 相关新闻
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    # order_by 排序 浏览量和发布时间
    stmt = select(News).where(News.id != news_id,
                              News.category_id == category_id,
                              ).order_by(
        News.views.desc(),  # 默认升序，desc降序
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    # return result.scalars().all()
    # 列表推导式 推导出新闻的核心数据，不要全量数据
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in related_news]
