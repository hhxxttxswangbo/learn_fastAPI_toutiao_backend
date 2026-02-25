"""
头条后端应用 - 主程序文件

这个文件是 FastAPI 应用的入口点，负责：
1. 创建 FastAPI 应用实例
2. 配置跨域资源共享（CORS）中间件
3. 注册各个功能模块的路由
4. 定义根路径的处理函数
"""

from fastapi import FastAPI
from routers import news, user
from fastapi.middleware.cors import CORSMiddleware

# 创建 FastAPI 应用实例
# app 是整个应用的核心对象，所有的路由、中间件配置都挂载在这个对象上
app = FastAPI()

# 配置跨域资源共享（CORS）中间件
# CORS 是浏览器安全机制，用于限制跨域请求
# 这里配置中间件允许前端应用从不同域访问后端 API
app.add_middleware(
    CORSMiddleware,  # 使用 FastAPI 的 CORS 中间件
    allow_origins=["*"],  # 允许的源：["*"] 表示允许所有来源访问（开发环境常用，生产环境应指定具体域名）
    allow_credentials=True,  # 允许携带凭证：True 表示允许请求携带 Cookie 和认证信息
    allow_methods=["*"],  # 允许的 HTTP 方法：["*"] 表示允许所有方法（GET、POST、PUT、DELETE 等）
    allow_headers=["*"],  # 允许的请求头：["*"] 表示允许所有请求头（如 Content-Type、Authorization 等）
)


# 定义根路径的路由处理函数
# 当用户访问 http://localhost:8000/ 时，会调用这个函数
@app.get("/")
def read_root():
    """
    根路径处理函数
    
    Returns:
        dict: 返回一个简单的 JSON 响应，用于测试服务是否正常运行
    """
    return {"Hello": "World"}


# 注册路由模块
# 将 news.py 中定义的路由注册到主应用中
# 这样所有在 news.router 中定义的路由都会被包含到应用中
# 例如：如果 news.py 中定义了 /categories，最终访问路径就是 /api/news/categories
app.include_router(news.router)
app.include_router(user.router)
