from datetime import datetime

from sqlalchemy import DateTime, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="更新时间"
    )


class Category(Base):
    # __tablename__ 要跟表名一样
    __tablename__ = "news_category"
    # 列要跟表里的一样
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类id")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")

    # 打印日志
    def __repr__(self):
        return f"<Category(id={self.id},name={self.name},sort_order={self.sort_order})>"
