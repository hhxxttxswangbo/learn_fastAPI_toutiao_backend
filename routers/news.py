"""
新闻相关的路由模块

这个文件定义了新闻相关的 API 接口（路由）
路由负责处理 HTTP 请求，调用业务逻辑，并返回响应

FastAPI 的路由系统：
- 使用装饰器（@router.get、@router.post 等）定义路由
- 支持依赖注入（Depends）自动获取数据库会话等资源
- 自动生成 API 文档（Swagger UI）

接口实现流程：
1. 模块化路由 → API 接口规范文档
2. 定义模型类 → 数据库表（数据库设计文档）
3. 在 crud 文件夹里面创建文件，封装操作数据库的方法
4. 在路由处理函数里面调用 crud 封装好的方法，响应结果
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news

# 创建路由对象
# APIRouter 用于组织路由，支持模块化开发
# prefix: 所有路由的前缀，这个路由器下的所有接口都会加上这个前缀
# tags: 用于在 API 文档中分组，相同标签的接口会显示在一起
router = APIRouter(prefix="/api/news", tags=["news"])


# 例如：定义的路由是 /categories，实际访问路径是 /api/news/categories


@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    获取新闻分类列表接口
    
    当客户端发送 GET 请求到 /api/news/categories 时，会调用这个函数
    
    Args:
        skip (int, optional): 跳过的记录数（分页偏移），默认为 0
                            从查询参数中获取，例如：/categories?skip=10
        limit (int, optional): 返回的最大记录数（每页大小），默认为 100
                             从查询参数中获取，例如：/categories?limit=10
        db (AsyncSession): 数据库会话对象，由 FastAPI 的依赖注入自动提供
                          Depends(get_db) 表示调用 get_db 函数获取会话
    
    Returns:
        dict: 标准的 API 响应格式，包含：
            - code: 状态码，200 表示成功
            - message: 响应消息
            - data: 实际数据（分类列表）
    
    请求示例：
        GET /api/news/categories?skip=0&limit=10
    
    响应示例：
        {
            "code": 200,
            "message": "Hello World",
            "data": [
                {"id": 1, "name": "科技", "sort_order": 1, ...},
                {"id": 2, "name": "娱乐", "sort_order": 2, ...}
            ]
        }
    
    工作流程：
        1. FastAPI 自动解析查询参数（skip、limit）
        2. 通过依赖注入获取数据库会话（db）
        3. 调用 crud 层的 get_categories 函数查询数据库
        4. 将查询结果封装成标准格式返回
    """
    # 调用 crud 层的函数查询数据库
    # 传入数据库会话和分页参数
    categories = await news.get_categories(db, skip, limit)

    # 返回标准格式的响应
    # 使用统一的响应格式，方便前端处理
    return {
        "code": 200,  # 状态码：200 表示成功
        "message": "获取新闻分类成功",  # 响应消息
        "data": categories  # 实际数据：分类列表
    }


@router.get("/list")
async def get_news_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * page_size
    new_list = await news.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    # has_more 跳过的 + 当前列表里面的数量 < 总量
    has_more = (offset + len(new_list)) < total
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": new_list,
            "total": total,
            "hasMore": has_more,
        }
    }


@router.get('/detail')
async def get_news_detail(news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)):
    # 获取新闻详情 + 浏览量 +1 + 相关新闻
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 浏览量
    news_view_res = await news.increase_news_views(db, news_detail.id)
    if not news_view_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        }
    }
