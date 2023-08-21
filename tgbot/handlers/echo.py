from aiogram import types
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.utils.markdown import hcode

router = Router()


@router.message(Command('get_id'))
async def get_id(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = f'user_id: {hcode(user_id)} || chat_id: {hcode(chat_id)}'
    await message.answer(text)

