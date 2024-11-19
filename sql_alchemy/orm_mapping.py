# Declarative Mapping
# from typing import Optional
# from sqlalchemy import Integer, String, ForeignKey
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# class Base(DeclarativeBase):
#     pass


# class User(Base):
#     __tablename__ = "user"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]
#     fullname: Mapped[str] = mapped_column(String(30))
#     nickname: Mapped[Optional[str]]


# imperative maping
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()

user_table = Table(
    "user",
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("fullname", String(50)),
    Column("nickname", String(12)),
)


class User:
    pass


mapper_registry.map_imperatively(User, user_table)

address_table = Table(
    "address",
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("email_address", String(50)),
)


class Address:
    pass


mapper_registry.map_imperatively(Address, address_table)

mapper_registry.map_imperatively(
    User,
    user_table,
    properties={"addresses": relationship(Address, backref="user")},
)
