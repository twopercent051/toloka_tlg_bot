from typing import Optional

from aiogram.types import Message, User, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.handlers.user.inline import MainInline
from tgbot.middlewares.black_list import BlockUserMiddleware
from tgbot.misc.states import UsersFSM
from tgbot.models.json_config import get_config
from tgbot.models.sql_connector import UsersDAO

router = Router()
router.message.outer_middleware(BlockUserMiddleware())
router.callback_query.outer_middleware(BlockUserMiddleware())

inline = MainInline()


async def start_render(user: User, command: Optional[CommandObject] = None):
    user_profile = await UsersDAO.get_one_or_none(user_id=str(user.id))
    username = f"@{user.username}" if user.username else ""
    if user_profile:
        balance = user_profile["balance"]
    else:
        await UsersDAO.create(user_id=str(user.id), username=username)
        if command:
            referer_id = command.args
            if referer_id:
                referer = await UsersDAO.get_one_or_none(user_id=referer_id)
                if referer:
                    referal_price = get_config(key="referal_price")
                    referer_price = get_config(key="referer_price")
                    await UsersDAO.update_by_user_id(user_id=str(user.id),
                                                     referer_id=command.args,
                                                     balance=referer_price)
                    await UsersDAO.update_balance(user_id=referer_id, delta_balance=referal_price)
                    referer_text = f"Вам начислено {referer_price} за приглашённого участника 🎉"
                    referal_text = f"Вам начислено {referal_price} за вступление по ссылке-приглашению 🎉"
                    await bot.send_message(chat_id=referer_id, text=referer_text)
                    await bot.send_message(chat_id=user.id, text=referal_text)
        user_profile = await UsersDAO.get_one_or_none(user_id=str(user.id))
        balance = user_profile["balance"]
    text = f"ГЛАВНОЕ МЕНЮ.\nТекущий баланс {balance} баллов"
    kb = inline.main_menu_kb()
    await bot.send_message(chat_id=user.id, text=text, reply_markup=kb)


@router.message(Command("start"))
async def user_start(message: Message, command: CommandObject, state: FSMContext):
    await start_render(user=message.from_user, command=command)
    await state.set_state(UsersFSM.home)


@router.callback_query(F.data == "home")
async def user_start(callback: CallbackQuery, state: FSMContext):
    await start_render(user=callback.from_user)
    await state.set_state(UsersFSM.home)
    await bot.answer_callback_query(callback.id)



