import json
from datetime import datetime
from typing import Literal

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.handlers.user.inline import GetWorkInline
from tgbot.middlewares.black_list import BlockUserMiddleware
from tgbot.misc.states import UsersFSM
from tgbot.models.json_config import get_config
from tgbot.models.sql_connector import UsersDAO, FollowingsDAO, RepostsDAO

router = Router()
router.message.outer_middleware(BlockUserMiddleware())
router.callback_query.outer_middleware(BlockUserMiddleware())

inline = GetWorkInline()


def get_jobs(jobs: list, job_type: Literal["following", "repost"], user_id: str):
    price = get_config(key=f"{job_type}s_worker_price")
    lang_dict = dict(following="Подписка", repost="Репост")
    result = []
    for item in list(filter(lambda x: x["author_id"] != user_id, jobs)):
        user_ids = [i["user_id"] for i in item["users"]]
        res_dict = {}
        if user_id not in user_ids:
            res_dict["id"] = item["id"]
            res_dict["create_dtime"] = item["create_dtime"]
            res_dict["type"] = job_type
            res_dict["price"] = price
            res_dict["ru_title"] = lang_dict[job_type]
            result.append(res_dict)
    return result


@router.callback_query(F.data == "get_work")
async def get_work_block(callback: CallbackQuery):
    followings = await FollowingsDAO.get_many(status="on")
    reposts = await RepostsDAO.get_many(status="on")
    followings = get_jobs(jobs=followings, job_type="following", user_id=str(callback.from_user.id))
    reposts = get_jobs(jobs=reposts, job_type="repost", user_id=str(callback.from_user.id))
    followings.extend(reposts)
    job_list = sorted(followings, key=lambda x: x["create_dtime"])
    text = "Выберите задание для выполнения"
    kb = inline.works_list_kb(jobs=job_list)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "job_profile")
async def get_work_block(callback: CallbackQuery, state: FSMContext):
    job_type = callback.data.split(":")[1]
    job_id = int(callback.data.split(":")[2])
    price = get_config(key=f"{job_type}s_worker_price")
    if job_type == "following":
        job_profile = await FollowingsDAO.get_one_or_none(id=job_id)
        text = [
            f"Для выполнения задания необходимо вступить в сообщество {job_profile['chat_link']}",
            "Вступите в сообщество и нажмите \"Проверить\"",
            f"Награда: {price} 💰"
        ]
        kb = inline.accept_work_kb(job_type=job_type, job_id=job_id)
    else:  # repost
        job_profile = await RepostsDAO.get_one_or_none(id=job_id)
        text = [
            "Для выполнения задания необходимо разместить в вашей группе или канале сообщение. Чтобы мы могли " 
            "проверить выполнение задания, вам необходимо сделать бота участником группы (канала). В течении " 
            "нескольких дней бот автоматически удалится. ",
            f"Награда: {price} 💰"
        ]
        await callback.message.answer(job_profile["repost_msg"])
        await callback.message.answer(text="Отправьте ссылку на группу или канал, в которую добавили бота")
        kb = None
        await state.set_state(UsersFSM.get_work_repost_url)
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


async def accept_following(user_id: str, price: int, job_profile):
    is_user = list(filter(lambda x: x["user_id"] == user_id, job_profile["users"]))
    if len(is_user) > 0:
        text = "Вы выполнили эту задачу ранее"
        kb = inline.home_kb()
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)
        return
    await UsersDAO.update_balance(user_id=user_id, delta_balance=price)
    user_job_dict = dict(user_id=user_id, dtime=int(datetime.utcnow().timestamp()), status="created")
    users_data = job_profile["users"]
    users_data.append(user_job_dict)
    await FollowingsDAO.update_by_id(item_id=job_profile["id"], users=users_data)
    text = f"Отлично. Вам начислено {price} 💰. Не покидайте сообщество, в противном случае награда " \
           f"будет списана, а вы заблокированы"
    kb = inline.home_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "proof_following")
async def get_work_block(callback: CallbackQuery):
    job_id = int(callback.data.split(":")[1])
    job_profile = await FollowingsDAO.get_one_or_none(id=job_id)
    price = get_config(key=f"followings_worker_price")
    await bot.answer_callback_query(callback.id)
    try:
        chat_member = await bot.get_chat_member(chat_id=job_profile["chat_link"], user_id=int(callback.from_user.id))
        user_status = chat_member.status
        if user_status in ["creator", "administrator", "member"]:
            await accept_following(user_id=str(callback.from_user.id), price=price, job_profile=job_profile)
        else:
            text = "К сожалению не удалось подтвердить вашу подписку. Убедитесь, что вы вступили в нужное " \
                   "сообщество и повторите проверку"
            kb = inline.accept_work_kb(job_type="following", job_id=job_id)
            await callback.message.answer(text, reply_markup=kb)
    except TelegramBadRequest:
        await accept_following(user_id=str(callback.from_user.id), price=price, job_profile=job_profile)


@router.message(F.text, UsersFSM.get_work_repost_url)
async def get_wok_block(message: Message, state: FSMContext):
    url = message.text
    kb = inline.home_kb()
    if url[0] != "@":
        try:
            url = f"@{url.split('/')[-1]}"
        except IndexError:
            text = "Невалидный URL. Проверьте ссылку и введите ещё раз"
            await message.answer(text, reply_markup=kb)
            return
    chat_population = await bot.get_chat_member_count(chat_id=url)

