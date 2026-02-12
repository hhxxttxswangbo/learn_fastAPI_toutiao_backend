"""
新闻模型模块

这个文件定义了新闻相关的数据库模型（Model）
模型是 Python 类，用于映射数据库表，通过 ORM（对象关系映射）操作数据库

模型的作用：
1. 定义数据库表结构（字段、类型、约束等）
2. 提供类型提示，提高代码可读性
3. 通过面向对象的方式操作数据库，而不是直接写 SQL

使用 SQLAlchemy 2.0 的新式声明语法（Mapped 和 mapped_column）
"""

from datetime import datetime

from sqlalchemy import DateTime, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    所有模型类的基类
    
    DeclarativeBase 是 SQLAlchemy 2.0 提供的声明式基类
    所有模型类都需要继承这个基类，才能被 SQLAlchemy 识别为模型
    
    这个基类定义了所有表共有的字段：
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    # 创建时间字段
    # Mapped[datetime] 表示这个字段的类型是 datetime
    # mapped_column 定义列的属性
    created_at: Mapped[datetime] = mapped_column(
        DateTime,  # 字段类型：日期时间类型
        default=datetime.now,  # 默认值：创建记录时自动设置为当前时间
        comment="创建时间"  # 字段注释，会同步到数据库
    )

    # 更新时间字段
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,  # 字段类型：日期时间类型
        default=datetime.now,  # 默认值：创建记录时自动设置为当前时间
        comment="更新时间"  # 字段注释，会同步到数据库
    )


class Category(Base):
    """
    新闻分类模型类
    
    这个类对应数据库中的 news_category 表
    继承自 Base，自动获得 created_at 和 updated_at 字段
    
    属性说明：
        id: 分类的唯一标识符（主键）
        name: 分类名称（唯一，不能为空）
        sort_order: 排序值（用于控制显示顺序）
    """
    # 指定对应的数据库表名
    # __tablename__ 必须与数据库中的实际表名一致
    __tablename__ = "news_category"

    # id 字段：主键
    # Mapped[int] 表示这个字段的类型是 int
    # mapped_column 定义列的属性
    id: Mapped[int] = mapped_column(
        Integer,  # 字段类型：整数类型
        primary_key=True,  # 主键：True 表示这是表的主键，唯一标识一条记录
        autoincrement=True,  # 自增：True 表示数据库自动为这个字段生成递增的值（1, 2, 3, ...）
        comment="分类id"  # 字段注释，会同步到数据库
    )

    # name 字段：分类名称
    name: Mapped[str] = mapped_column(
        String(50),  # 字段类型：字符串类型，最大长度 50
        unique=True,  # 唯一约束：True 表示这个字段的值在整个表中必须唯一（不能有重复的分类名）
        nullable=False,  # 非空约束：False 表示这个字段不能为空（必须有值）
        comment="分类名称"  # 字段注释，会同步到数据库
    )

    # sort_order 字段：排序值
    sort_order: Mapped[int] = mapped_column(
        Integer,  # 字段类型：整数类型
        default=0,  # 默认值：0
        nullable=False,  # 非空约束：False 表示这个字段不能为空
        comment="排序"  # 字段注释，会同步到数据库
    )

    # 定义 __repr__ 方法
    # __repr__ 是 Python 的魔术方法，用于定义对象的字符串表示
    # 当打印对象或在调试器中查看对象时，会调用这个方法
    def __repr__(self):
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串表示，包含 id、name 和 sort_order
        """
        return f"<Category(id={self.id},name={self.name},sort_order={self.sort_order})>"
