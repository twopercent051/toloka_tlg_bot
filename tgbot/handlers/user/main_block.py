from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(Command('start'))
async def user_start(message: Message):
    await message.answer('Доступ в бота возможен только из админской группы')


@router.message(F.text)
async def user_start(message: Message):
    await message.answer('Доступ в бота возможен только из админской группы')
