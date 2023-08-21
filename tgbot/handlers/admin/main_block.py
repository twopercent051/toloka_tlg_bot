from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.filters.state import StateFilter

from create_bot import bot
from .filters import AdminFilter
from .inline import InlineKeyboard
from tgbot.misc.states import AdminFSM
from tgbot.models.redis_connector import RedisConnector as rds

router = Router()
router.message.filter(AdminFilter())


@router.message(Command('start'), StateFilter('*'))
async def admin_start_msg(message: Message, state: FSMContext):
    text = 'Привет, хозяева. Это главное меню. Пока тут можно только выбрать ключевые слова'
    kb = inline_kb.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == 'home', StateFilter('*'))
async def admin_start_clb(callback: CallbackQuery, state: FSMContext):
    text = 'Привет, хозяева. Это главное меню. Пока тут можно только выбрать ключевые слова'
    kb = inline_kb.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == 'keywords', AdminFSM.home)
async def keywords_list(callback: CallbackQuery, state: FSMContext):
    kw_list = await rds.get_kw_list()
    if kw_list:
        text = ['<b>Список ключевых слов:</b>\n']
        for row in kw_list:
            text.append(f'<i>{row}</i>')
        text.append('\nДля изменения списка отправьте его ответным сообщением. Каждое ключевое выражение отдельной '
                    'строкой через ENTER. Поиск идет по вхождениям неполных'
                    'слов. Например: по ключевому слову <i>карт</i> будут найдены сообщения со словами <i>карты, '
                    'карточка, картон</i>')
    else:
        text = [
            '<b>Вы не задали ключевые слова.</b>',
            '\nДля изменения списка отправьте его ответным сообщением. Поиск идет по вхождениям неполных Каждое '
            'ключевое выражение отдельной строкой через ENTER. Поиск идет по вхождениям неполных'
            'слов. Например: по ключевому слову <i>карт</i> будут найдены сообщения со словами <i>карты, '
            'карточка, картон</i>'
        ]
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.get_kw)
    await callback.message.answer('\n'.join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.get_kw)
async def get_kw(message: Message, state: FSMContext):
    new_kw = message.text.split('\n')
    await rds.update_kw_list(new_kw)
    text = 'Изменения сохранены.'
    kb = inline_kb.kw_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)
