import json

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router

from create_bot import bot
from tgbot.handlers.admin.filters import AdminFilter
from tgbot.handlers.admin.inline import SettingsInline
from tgbot.misc.states import AdminFSM

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = SettingsInline()


def json_render(data: dict, key: str) -> int:
    return data[key] if data.keys().__contains__(key) else 0


texts_dict = dict(one_mark_price="Цена одного балла",
                  one_day_limit="Лимит заданий в день",
                  followings_employer_price="Подписки: цена для заказчика",
                  reposts_employer_price="Репосты: цена для заказчика",
                  followings_worker_price="Подписки: цена для исполнителя",
                  reposts_worker_price="Репосты: цена для исполнителя",
                  referal_price="Вознаграждение приглашённому",
                  referer_price="Вознаграждение пригласившему",
                  punish="Штраф за отписку",
                  verif_duration="Срок верификации подписки или репоста (суток)")


@router.callback_query(F.data == "settings")
async def settings_block(callback: CallbackQuery):
    with open("config.json") as config_file:
        data = json.loads(config_file.read())
    text = ["<b>Действующие настройки:</b>\n"]
    for t in texts_dict:
        text.append(f"<i>{texts_dict[t]}</i>: {json_render(data, key=t)}")
    text.append("\nВыберите что нужно поменять")
    kb = inline.settings_menu_kb(texts_dict=texts_dict)
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "setting")
async def settings_block(callback: CallbackQuery, state: FSMContext):
    clb_data = callback.data.split(':')[1]
    with open("config.json") as config_file:
        f = config_file.read()

        data = json.loads(f)
    text = f"<b>{texts_dict[clb_data]}</b>\n{json_render(data=data, key=clb_data)}\nВведите новое значение"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.settings)
    await state.update_data(setting=clb_data)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.settings)
async def settings_block(message: Message, state: FSMContext):
    kb = inline.home_kb()
    try:
        value = int(message.text)
    except ValueError:
        await message.answer("Введите число", reply_markup=kb)
        return
    state_data = await state.get_data()
    setting = state_data["setting"]
    with open("config.json") as config_file:
        data = json.loads(config_file.read())
    data[setting] = value
    with open("config.json", 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
    text = "Настройки сохранены"
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


