# 数据类型校验
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")


# /add为post请求，需要添加pydantic
class AddFavoriteRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")
