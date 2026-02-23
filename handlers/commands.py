import telebot
import time
import config
from utils.keyboards import get_main_menu_keyboard
from database.loader import DataLoader

def register_commands(bot: telebot.TeleBot, data_loader: DataLoader):
    
    @bot.message_handler(commands=['start'])
    def start_message(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username
        
        print(f"🟢 /start от @{username}")
        
        # Проверка доступа
        if not username:
            bot.send_message(chat_id, config.MESSAGES['no_username'])
            return
        
        if not data_loader.is_user_allowed(username):
            bot.send_message(chat_id, config.MESSAGES['access_denied'])
            return
        
        # Проверка данных
        if data_loader.data is None:
            bot.send_message(chat_id, config.MESSAGES['data_loading'])
            if not data_loader.load_data():
                bot.send_message(chat_id, config.MESSAGES['error'])
                return
        
        bot.send_message(
            chat_id, 
            config.MESSAGES['welcome'], 
            reply_markup=get_main_menu_keyboard()
        )
    
    @bot.message_handler(commands=['status'])
    def status_message(message):
        chat_id = message.chat.id
        username = message.from_user.username
        
        if not username or not data_loader.is_user_allowed(username):
            bot.send_message(chat_id, config.MESSAGES['access_denied'])
            return
        
        status_text = "📊 **СТАТУС БОТА:**\n\n"
        
        if data_loader.data is None:
            status_text += "❌ Данные: **НЕ ЗАГРУЖЕНЫ**\n"
        elif data_loader.data.empty:
            status_text += "⚠️ Данные: **ПУСТЫ**\n"
        else:
            status_text += f"✅ Данные: **{len(data_loader.data)}** записей\n"
        
        status_text += f"👥 Разрешено пользователей: {len(data_loader.allowed_users)}\n"
        status_text += f"🕐 Последнее обновление: {data_loader.last_update_time}\n"
        
        bot.send_message(
            chat_id, 
            status_text, 
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
    
    @bot.message_handler(commands=['reload'])
    def reload_data(message):
        chat_id = message.chat.id
        username = message.from_user.username
        
        if not username or not data_loader.is_user_allowed(username):
            bot.send_message(chat_id, config.MESSAGES['access_denied'])
            return
        
        bot.send_message(chat_id, "🔄 Перезагружаю данные...")
        if data_loader.load_data():
            bot.send_message(
                chat_id, 
                config.MESSAGES['reload_success'].format(count=len(data_loader.data)),
                reply_markup=get_main_menu_keyboard()
            )
        else:
            bot.send_message(chat_id, config.MESSAGES['reload_error'])