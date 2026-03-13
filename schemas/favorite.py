# 数据类型校验
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")


# /add为post请求，需要添加pydantic
class AddFavoriteRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 规划两个类：新闻模型类 + 收藏的模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# 收藏列表接口相应的模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
