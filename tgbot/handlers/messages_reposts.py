import json
from datetime import datetime
from typing import Literal

from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, Command
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.handlers.user.inline import GetWorkInline
from tgbot.middlewares.black_list import RepostTextsMiddleware
from tgbot.misc.states import UsersFSM
from tgbot.models.json_config import get_config
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import UsersDAO, FollowingsDAO, RepostsDAO

router = Router()
router.message.outer_middleware(RepostTextsMiddleware())


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def test(event: ChatMemberUpdated):
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.type in ["group", "supergroup"]:
        text = f"Мы заметили, что вы добавили бота в группу {chat_info.title}.\nПрежде чем отправить сообщение, " \
               f"убедитесь, что бот имеет разрешение на чтение сообщений"
    elif chat_info.type == "channel":
        text = f"Мы заметили, что вы добавили бота в группу {chat_info.title}."
    else:
        return
    redis_data = dict(user_id=event.from_user.id, chat_id=chat_info.id)
    RedisConnector.add_item(redis_db_name="repost_chats", item=redis_data)
    await bot.send_message(chat_id=event.from_user.id, text=text)


@router.message(F.text)
async def messages_reposts_block(message: Message):
    reposts_texts = RedisConnector.get_list(redis_db_name="repost_texts")
    print(message.text)
    if message.text in reposts_texts:
        chats = RedisConnector.get_list(redis_db_name="repost_chats")
        for chat in chats:
            if chat["chat_id"] == message.chat.id and chat["user_id"] == message.from_user.id:
                order = await RepostsDAO.get_one_or_none(repost_msg=message.text, status="on")
                if order:
                    price = get_config(key=f"reposts_worker_price")
                    text = f"Вы выполнили задание. Ваш баланс пополнен на {price} 💰. Не удаляйте сообщение и бота"
                    order_dict = dict(user_id=message.from_user.id,
                                      dtime=int(datetime.utcnow().timestamp()),
                                      chat_id=message.chat.id,
                                      message_id=message.message_id,
                                      status="created")
                    users_data = order["users"]
                    users_data.append(order_dict)
                    await RepostsDAO.update_by_id(item_id=order["id"], users=users_data)
                    await UsersDAO.update_balance(user_id=str(message.from_user.id), delta_balance=price)
                    await bot.send_message(chat_id=message.from_user.id, text=text)
