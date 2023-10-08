from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from tgbot.models.redis_connector import RedisConnector


class BlockUserMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        if str(event.from_user.id) not in RedisConnector.get_list(redis_db_name="black_list"):
            return await handler(event, data)


class RepostTextsMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        if event.text in RedisConnector.get_list(redis_db_name="repost_texts"):
            return await handler(event, data)
