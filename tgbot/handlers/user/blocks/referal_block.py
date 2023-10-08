from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram import F, Router
from aiogram.utils.markdown import hcode

from create_bot import bot
from tgbot.handlers.user.inline import MainInline
from tgbot.middlewares.black_list import BlockUserMiddleware
from tgbot.models.json_config import get_config

router = Router()
router.message.outer_middleware(BlockUserMiddleware())
router.callback_query.outer_middleware(BlockUserMiddleware())

inline = MainInline()


@router.callback_query(F.data == "referal")
async def referal_block(callback: CallbackQuery):
    link = await create_start_link(bot=bot, payload=callback.from_user.id)
    referal_price = get_config(key="referal_price")
    referer_price = get_config(key="referer_price")
    text = [
        "Чтобы пригласить друга по реферальной программе, отправьте ему ссылку-приглашение:",
        hcode(link),
        f"Вы получите {referer_price} баллов, а ваш друг {referal_price}"
    ]
    kb = inline.home_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)
