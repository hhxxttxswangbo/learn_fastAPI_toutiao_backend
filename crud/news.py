from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.news import Category

async def get_categories(db: AsyncSession,skip: int = 0,limit: int = 100):
   # 查询数据库语句
   stmt = select(Category).offset(skip).limit(limit)
   # 让db数据库执行
   result = await db.execute(stmt)
   # 提取结果 return
   return result.scalars().all()