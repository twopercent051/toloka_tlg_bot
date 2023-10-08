from typing import Literal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class MainInline:

    def __init__(self):
        self._home_button = InlineKeyboardButton(text="🏡 На главную", callback_data="home")

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="🛠 Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="🧑‍🦰 Пользователи", callback_data="users_profile")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def home_kb(self):
        keyboard = [[self._home_button]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class SettingsInline(MainInline):

    def settings_menu_kb(self, texts_dict: dict):
        keyboard = []
        for text in texts_dict:
            keyboard.append([InlineKeyboardButton(text=texts_dict[text], callback_data=f"setting:{text}")])
        keyboard.append([self._home_button])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class UsersProfileInline(MainInline):

    def user_profile_kb(self, user_id: str | int, status: Literal["active", "blocked"]):
        status_dict = dict(active=("blocked", "🟥"), blocked=("active", "🟩"))
        keyboard = [
            [InlineKeyboardButton(text="🛠 Баланс", callback_data=f"balance:{user_id}")],
            [InlineKeyboardButton(text=f"{status_dict[status][1]} Статус",
                                  callback_data=f"set_status:{user_id}:{status_dict[status][0]}")],
            [InlineKeyboardButton(text="✉️ Отправить сообщение", callback_data=f"send_message:{user_id}")],
            [self._home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def message_answer_kb():
        keyboard = [[InlineKeyboardButton(text="📞 Ответить", callback_data="support")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
