import telebot
from typing import List
import config
from utils.callback_helpers import create_callback_data

def get_main_menu_keyboard():
    """Создает клавиатуру с главным меню"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start = telebot.types.KeyboardButton(config.MENU_BUTTONS['start'])
    btn_continue = telebot.types.KeyboardButton(config.MENU_BUTTONS['continue'])
    markup.add(btn_start, btn_continue)
    return markup

def get_answer_keyboard(options: List[str]):
    """Создает inline клавиатуру с вариантами ответов (вертикально)"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for option in options:
        # Используем безопасный callback_data
        callback_data = create_callback_data('answer', option)
        button = telebot.types.InlineKeyboardButton(
            text=option, 
            callback_data=callback_data
        )
        markup.add(button)
    return markup

def get_position_keyboard(options: List[str]):
    """Создает inline клавиатуру с вариантами должностей"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for option in options:
        # Используем безопасный callback_data
        callback_data = create_callback_data('position', option)
        button = telebot.types.InlineKeyboardButton(
            text=option, 
            callback_data=callback_data
        )
        markup.add(button)
    return markup

def get_next_keyboard():
    """Создает клавиатуру с кнопкой Далее"""
    markup = telebot.types.InlineKeyboardMarkup()
    next_button = telebot.types.InlineKeyboardButton(
        text="➡️ Далее", 
        callback_data="next"
    )
    markup.add(next_button)
    return markup