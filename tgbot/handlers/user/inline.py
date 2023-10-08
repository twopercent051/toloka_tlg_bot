from typing import Literal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class MainInline:

    def __init__(self):
        self._home_button = InlineKeyboardButton(text="🏡 На главную", callback_data="home")

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="🛠 Выполнение заданий", callback_data="get_work")],
            [InlineKeyboardButton(text="📲 Разместить задание", callback_data="set_work")],
            [InlineKeyboardButton(text="➕ Реферальная программа", callback_data="referal")],
            [InlineKeyboardButton(text="❔ FAQ", callback_data="faq")],
            [InlineKeyboardButton(text="🧑‍💻 Поддержка", callback_data="support")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def home_kb(self):
        keyboard = [[self._home_button]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class SupportInline(MainInline):

    @staticmethod
    def message_answer_kb(user_id: int | str):
        keyboard = [[InlineKeyboardButton(text="📞 Ответить", callback_data=f"send_message:{user_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class SetWorkInline(MainInline):

    def type_work_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="Подписка на группу/канал", callback_data="set_work_type:followings")],
            [InlineKeyboardButton(text="Репост сообщения", callback_data="set_work_type:reposts")],
            [self._home_button],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def support_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="🛠 Выполнение заданий", callback_data="get_work")],
            [InlineKeyboardButton(text="🧑‍💻 Поддержка", callback_data="support")],
            [self._home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def accept_work_kb(self, set_type_work: Literal["followings", "reposts"]):
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Всё верно!", callback_data=f"accept_set_work:{set_type_work}"),
                self._home_button
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class GetWorkInline(MainInline):

    def works_list_kb(self, jobs: list):
        keyboard = []
        for job in jobs:
            keyboard.append([InlineKeyboardButton(text=f"{job['ru_title']} {job['price']} 💰",
                                                  callback_data=f"job_profile:{job['type']}:{job['id']}")])
        keyboard.append([self._home_button])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def accept_work_kb(self, job_id: int | str, job_type: Literal["following", "repost"]):
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Проверить", callback_data=f"proof_{job_type}:{job_id}"),
                self._home_button
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
