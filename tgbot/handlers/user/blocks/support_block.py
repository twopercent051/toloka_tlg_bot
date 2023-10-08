from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.handlers.user.inline import SupportInline
from tgbot.middlewares.black_list import BlockUserMiddleware
from tgbot.misc.states import UsersFSM

router = Router()
router.message.outer_middleware(BlockUserMiddleware())
router.callback_query.outer_middleware(BlockUserMiddleware())

inline = SupportInline()
admin_group = config.tg_bot.admin_group


@router.callback_query(F.data == "support")
async def support_block(callback: CallbackQuery, state: FSMContext):
    text = "Введите сообщение. Оно будет отправлено администратору с сохранением форматирования. Также можно " \
           "приложить одно фото, видео или документ"
    kb = inline.home_kb()
    await state.set_state(UsersFSM.send_message)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UsersFSM.send_message)
@router.message(F.photo, UsersFSM.send_message)
@router.message(F.video, UsersFSM.send_message)
@router.message(F.document, UsersFSM.send_message)
async def users_profile_block(message: Message, state: FSMContext):
    text = message.html_text
    kb = inline.message_answer_kb(user_id=message.from_user.id)
    if message.content_type == "text":
        await bot.send_message(chat_id=admin_group, text=text, reply_markup=kb)
    if message.content_type == "photo":
        await bot.send_photo(chat_id=admin_group, photo=message.photo[-1].file_id, caption=text, reply_markup=kb)
    if message.content_type == "video":
        await bot.send_video(chat_id=admin_group, video=message.video.file_id, caption=text, reply_markup=kb)
    if message.content_type == "document":
        await bot.send_document(chat_id=admin_group, document=message.document.file_id, caption=text, reply_markup=kb)
    text = "👍 Сообщение отправлено"
    kb = inline.home_kb()
    await state.set_state(UsersFSM.home)
    await message.answer(text, reply_markup=kb)
