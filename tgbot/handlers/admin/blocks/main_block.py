from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot, config
from tgbot.handlers.admin.filters import AdminFilter
from tgbot.handlers.admin.inline import MainInline
from tgbot.misc.states import AdminFSM


from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, JOIN_TRANSITION

from tgbot.models.sql_connector import UsersDAO, FollowingsDAO

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = MainInline()
admin_group = config.tg_bot.admin_group


@router.message(Command("test"))
async def test_block(message: Message):
    # url = "https://t.me/g5387o53g"
    # chat_id = f'@{url.split("/")[-1]}'
    # # chat = "@lentachold"
    # user = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
    # # bot_q = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
    # a = ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION)
    # # print(user)
    # print(user.status)
    # await bot.leave_chat(chat_id=chat_id)
    a = await bot.m





async def start_render(user_id: str | int):
    text = "Главное меню администратора бота"
    kb = inline.main_menu_kb()
    await bot.send_message(chat_id=admin_group, text=text, reply_markup=kb)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render(user_id=message.from_user.id)
    await state.set_state(AdminFSM.home)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render(user_id=callback.from_user.id)
    await state.set_state(AdminFSM.home)
    await bot.answer_callback_query(callback.id)
