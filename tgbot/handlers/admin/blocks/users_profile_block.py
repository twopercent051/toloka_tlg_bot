import os
from datetime import timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F, Router

from create_bot import bot, config
from tgbot.handlers.admin.filters import AdminFilter
from tgbot.handlers.admin.inline import UsersProfileInline
from tgbot.misc.states import AdminFSM
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import UsersDAO
from tgbot.services.excel import ExcelCreate

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = UsersProfileInline()
admin_group = config.tg_bot.admin_group


@router.callback_query(F.data == "users_profile")
async def users_profile_block(callback: CallbackQuery, state: FSMContext):
    users = await UsersDAO.get_many()
    text = f"Сейчас зарегистрировано <u>{len(users)}</u> пользователей. Чтобы открыть профиль пользователя введите " \
           f"его USER_ID"
    file_name = ExcelCreate.create_users(users=users)
    file = FSInputFile(path=file_name, filename=file_name)
    kb = inline.home_kb()
    await state.set_state(AdminFSM.users_profile)
    await callback.message.answer_document(document=file)
    await callback.message.answer(text, reply_markup=kb)
    os.remove(file_name)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.users_profile)
async def users_profile_block(message: Message, state: FSMContext):
    user = await UsersDAO.get_one_or_none(user_id=message.text.strip())
    if user:
        referals = await UsersDAO.get_many(referer_id=message.text.strip())
        status_dict = dict(blocked=("Заблокирован", "🟥"), active=("Активный", "🟩"))
        text = [
            f"USERNAME: {user['username']}",
            f"Дата регистрации: {(user['reg_dtime'] + timedelta(hours=3)).strftime('%d-%m-%Y %H:%M')}",
            f"Баланс: {user['balance']}",
            f"Статус: {status_dict[user['status']][1]} {status_dict[user['status']][0]}",
            f"Реферер: {user['referer_id']}",
            f"Кол-во рефералов: {len(referals)}",
        ]
        kb = inline.user_profile_kb(user_id=message.text.strip(), status=user["status"])
        await state.set_state(AdminFSM.home)
    else:
        text = ["Пользователь с таким USER_ID не найден. Попробуйте снова"]
        kb = inline.home_kb()
    await message.answer("\n".join(text), reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "balance")
async def users_profile_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split(":")[1]
    user = await UsersDAO.get_one_or_none(user_id=str(user_id))
    text = f"Текущий баланс пользователя: {user['balance']} баллов. Отправьте количество, на которое нужно " \
           f"пополнить баланс. (Для списания баллов отправьте число со знаком минус)"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.balance)
    await state.update_data(user_id=user_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.balance)
async def users_profile_block(message: Message, state: FSMContext):
    kb = inline.home_kb()
    try:
        value = int(message.text.strip())
    except ValueError:
        text = "Вы ввели не число. Попробуйте снова"
        await message.answer(text, reply_markup=kb)
        return
    state_data = await state.get_data()
    user_id = state_data["user_id"]
    await UsersDAO.update_balance(user_id=user_id, delta_balance=value)
    user = await UsersDAO.get_one_or_none(user_id=user_id)
    text = f"Обновлённый баланс: {user['balance']}"
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "set_status")
async def users_profile_block(callback: CallbackQuery):
    user_id = callback.data.split(":")[1]
    new_status = callback.data.split(":")[2]
    await UsersDAO.update_by_user_id(user_id=user_id, status=new_status)
    if new_status == "active":
        RedisConnector.delete_item(item=user_id, redis_db_name="black_list")
    else:  # blocked
        RedisConnector.add_item(item=user_id, redis_db_name="black_list")
    kb = inline.user_profile_kb(user_id=user_id, status=new_status)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "send_message")
async def users_profile_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split(":")[1]
    text = "Введите сообщение. Оно будет отправлено пользователю с сохранением форматирования. Также можно " \
           "приложить одно фото, видео или документ"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.send_message)
    await state.update_data(user_id=user_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.send_message)
@router.message(F.photo, AdminFSM.send_message)
@router.message(F.video, AdminFSM.send_message)
@router.message(F.document, AdminFSM.send_message)
async def users_profile_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data["user_id"]
    text = message.html_text
    kb = inline.message_answer_kb()
    if message.content_type == "text":
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)
    if message.content_type == "photo":
        await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=text, reply_markup=kb)
    if message.content_type == "video":
        await bot.send_video(chat_id=user_id, video=message.video.file_id, caption=text, reply_markup=kb)
    if message.content_type == "document":
        await bot.send_document(chat_id=user_id, document=message.document.file_id, caption=text, reply_markup=kb)
    text = "👍 Сообщение отправлено"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)
