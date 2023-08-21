from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineKeyboard:

    @classmethod
    def main_menu_kb(cls):
        keyboard = [[InlineKeyboardButton(text='Ключевые слова', callback_data='keywords')]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def home_kb(cls):
        keyboard = [[InlineKeyboardButton(text='🏡 Домой', callback_data='home')]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def kw_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text='Ключевые слова', callback_data='keywords'),
                InlineKeyboardButton(text='🏡 Домой', callback_data='home')
            ]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard
