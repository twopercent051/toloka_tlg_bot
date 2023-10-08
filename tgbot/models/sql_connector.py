from sqlalchemy import MetaData, DateTime, Column, Integer, String, JSON, select, insert, delete, update, TEXT
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker, as_declarative
from sqlalchemy.sql import expression

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()


class UtcNow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(UtcNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class UsersDB(Base):
    """Пользователи"""
    __tablename__ = "users"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    reg_dtime = Column(DateTime, nullable=False, server_default=UtcNow())
    balance = Column(Integer, nullable=False, server_default="0")
    disruptions = Column(Integer, nullable=False, server_default="0")
    status = Column(String, nullable=False, server_default="active")  # active blocked
    referer_id = Column(String, nullable=True)


class FollowingsDB(Base):
    """Подписки"""
    __tablename__ = "followings"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    create_dtime = Column(DateTime, nullable=False, server_default=UtcNow())
    author_id = Column(String, nullable=False)
    chat_link = Column(String, nullable=False)
    quantity = Column(Integer, nullable=True)
    status = Column(String, nullable=False, server_default="on")  # on off
    users = Column(JSON, nullable=False, server_default="[]")  # list(dict(user_id, dtime, status))


class RepostsDB(Base):
    """Подписки"""
    __tablename__ = "reposts"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    create_dtime = Column(DateTime, nullable=False, server_default=UtcNow())
    author_id = Column(String, nullable=False)
    repost_msg = Column(TEXT, nullable=False)
    quantity = Column(Integer, nullable=True)
    status = Column(String, nullable=False, server_default="on")  # on off
    users = Column(JSON, nullable=False, server_default="[]")  # list(dict(user_id, dtime, chat_id, message_id))


class BaseDAO:
    """Класс взаимодействия с БД"""
    model = None

    @classmethod
    async def get_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by).limit(1)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_many(cls, **filter_by) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data)
            result = await session.execute(stmt)
            await session.commit()
            return result.mappings().one_or_none()

    @classmethod
    async def delete(cls, **data):
        async with async_session_maker() as session:
            stmt = delete(cls.model).filter_by(**data)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def update_by_id(cls, item_id: int, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(id=item_id)
            await session.execute(stmt)
            await session.commit()


class UsersDAO(BaseDAO):
    model = UsersDB

    @classmethod
    async def update_by_user_id(cls, user_id: str, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(user_id=user_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def update_balance(cls, user_id: str, delta_balance: int):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(balance=cls.model.balance + delta_balance).filter_by(user_id=user_id).\
                returning()
            await session.execute(stmt)
            await session.commit()


class FollowingsDAO(BaseDAO):
    model = FollowingsDB


class RepostsDAO(BaseDAO):
    model = RepostsDB
