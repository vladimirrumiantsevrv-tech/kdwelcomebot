import telebot
import config
from utils.keyboards import get_main_menu_keyboard
from database.loader import DataLoader
from session.manager import SessionManager
from handlers.game import send_question

def register_menu_handlers(
    bot: telebot.TeleBot, 
    data_loader: DataLoader,
    session_manager: SessionManager
):
    
    @bot.message_handler(func=lambda message: message.text in [
        config.MENU_BUTTONS['start'], 
        config.MENU_BUTTONS['continue']
    ])
    def handle_menu_buttons(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username
        
        if not username or not data_loader.is_user_allowed(username):
            bot.send_message(chat_id, config.MESSAGES['access_denied'])
            return
        
        if message.text == config.MENU_BUTTONS['start']:
            # Очищаем сессию и начинаем новую игру
            session_manager.clear_session(user_id)
            send_question(bot, chat_id, user_id, data_loader, session_manager)
        
        elif message.text == config.MENU_BUTTONS['continue']:
            if session_manager.session_exists(user_id):
                send_question(bot, chat_id, user_id, data_loader, session_manager)
            else:
                bot.send_message(
                    chat_id, 
                    config.MESSAGES['no_session'],
                    reply_markup=get_main_menu_keyboard()
                )