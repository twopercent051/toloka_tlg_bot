from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.handlers.user.inline import SetWorkInline
from tgbot.middlewares.black_list import BlockUserMiddleware
from tgbot.misc.states import UsersFSM
from tgbot.models.json_config import get_config
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import UsersDAO, FollowingsDAO, RepostsDAO

router = Router()
router.message.outer_middleware(BlockUserMiddleware())
router.callback_query.outer_middleware(BlockUserMiddleware())

inline = SetWorkInline()


@router.callback_query(F.data == "set_work")
async def set_work_block(callback: CallbackQuery):
    text = "Вы можете заказать через бота привлечение участников вашей группы или канала, а также репост сообщения в " \
           "каналах и группах других пользователей"
    kb = inline.type_work_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "set_work_type")
async def set_work_block(callback: CallbackQuery, state: FSMContext):
    work_type = callback.data.split(":")[1]
    user = await UsersDAO.get_one_or_none(user_id=str(callback.from_user.id))
    balance = user["balance"]
    if work_type == "followings":
        price = get_config(key="followings_employer_price")
        text = f"Цена одного подписчика составляет {price} баллов. Введите количество требуемых подписчиков " \
               f"(сейчас у вас {balance} баллов)"
    else:  # reposts
        price = get_config(key="reposts_employer_price")
        text = f"Цена одного репоста составляет {price} баллов. Введите количество репостов " \
               f"(сейчас у вас {balance} баллов)"
    await state.update_data(set_work_type=work_type)
    await state.set_state(UsersFSM.quantity)
    kb = inline.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UsersFSM.quantity)
async def set_work_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    set_work_type = state_data["set_work_type"]
    kb = inline.home_kb()
    try:
        quantity = int(message.text)
        if quantity <= 0:
            text = "Введите пожалуйста число больше нуля"
            await message.answer(text, reply_markup=kb)
            return
    except ValueError:
        text = "Введите пожалуйста целое число"
        await message.answer(text, reply_markup=kb)
        return
    user = await UsersDAO.get_one_or_none(user_id=str(message.from_user.id))
    balance = user["balance"]
    price = get_config(key=f"{set_work_type}_employer_price")
    if balance < quantity * price:
        text = "У вас недостаточно средств на балансе. Вы можете заработать баллы, выполняя задания или запросить в " \
               "поддержке"
        kb = inline.support_kb()
    else:
        if set_work_type == "followings":
            text = "👍 Здорово! Теперь пришлите нам ссылку на группу или канал, куда будем приглашать " \
                   "участников\n\n<u>Чтобы мы могли проконтролировать вступление в вашу группу или канал другого " \
                   "участника вам необходимо добавить этого бота в вашу группу или канал. Бот автоматически удалится " \
                   "когда верифицирует всех подписчиков. Если этого не сделать, мы не сможем гарантировать, что " \
                   "реальное количество подписчиков соответствует заявленному</u>"

            await state.set_state(UsersFSM.followings_url)
        else:
            text = "👍 Здорово! Теперь пришлите нам сообщение, которое будут репостить другие участники"
            await state.set_state(UsersFSM.repost_text)
    await state.update_data(quantity=quantity, price=price)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, UsersFSM.followings_url)
async def set_work_block(message: Message, state: FSMContext):
    url = message.text
    kb = inline.home_kb()
    if url[0] != "@":
        try:
            url = f"@{url.split('/')[-1]}"
        except IndexError:
            text = "Невалидный URL. Проверьте ссылку и введите ещё раз"
            await message.answer(text, reply_markup=kb)
            return
    state_data = await state.get_data()
    quantity = state_data["quantity"]
    price = state_data["price"]
    annotation = [
        f"<u>Группа (канал):</u> {url}",
        f"<u>Количество:</u> {quantity}",
        f"<u>Цена:</u> {price}",
        f"<u>Общая стоимость:</u> {quantity * price}",
    ]
    try:
        await bot.get_chat_member(chat_id=url, user_id=int(message.from_user.id))
        text = ["👍 Отлично! Проверьте введённые данные и можем публиковать задание:\n"]
        text.extend(annotation)
        kb = inline.accept_work_kb(set_type_work="followings")
    except TelegramBadRequest as ex:
        if ex.message.split(":")[-1].strip() == "user not found":
            text = [
                "<u>Видимо вы не добавили бота в группу или канал. Мы не сможем убедиться, что другие участники "
                "стали вашими подписчиками</u>",
                "Тем не менее, Вы всё равно можете опубликовать задание, проверьте данные:\n",
            ]
            text.extend(annotation)
            kb = inline.accept_work_kb(set_type_work="followings")
        else:  # chat not found
            text = "Я не нашёл такого чата или канала в Телеграме 🤷\nПроверьте ссылку и введите ещё раз"
            await message.answer(text, reply_markup=kb)
            return
    await message.answer("\n".join(text), reply_markup=kb)
    await state.update_data(url=url)
    await state.set_state(UsersFSM.home)


@router.message(F.text, UsersFSM.repost_text)
async def set_work_block(message: Message, state: FSMContext):
    await state.update_data(repost_msg=message.text)
    state_data = await state.get_data()
    quantity = state_data["quantity"]
    price = state_data["price"]
    text = [
        "👍 Отлично! Проверьте введённые данные и можем публиковать задание:\n",
        message.text,
        f"<u>Количество:</u> {quantity}",
        f"<u>Цена:</u> {price}",
        f"<u>Общая стоимость:</u> {quantity * price}",
    ]
    kb = inline.accept_work_kb(set_type_work="reposts")
    await message.answer("\n".join(text), reply_markup=kb)
    await state.set_state(UsersFSM.home)


@router.callback_query(F.data.split(":")[0] == "accept_set_work")
async def set_work_block(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    set_type_work = callback.data.split(":")[1]
    state_data = await state.get_data()
    quantity = state_data["quantity"]
    price = state_data["price"]
    if set_type_work == "followings":
        url = state_data["url"]
        await FollowingsDAO.create(author_id=user_id, chat_link=url, quantity=quantity)
    else:  # reposts
        repost_msg = state_data["repost_msg"]
        await RepostsDAO.create(author_id=user_id, repost_msg=repost_msg, quantity=quantity)
        RedisConnector.add_item(redis_db_name="repost_texts", item=repost_msg)
    total_cost = - (quantity * price)
    await UsersDAO.update_balance(user_id=user_id, delta_balance=total_cost)
    text = "👍 Задание опубликовано"
    kb = inline.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)
