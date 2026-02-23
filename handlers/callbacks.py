import telebot
from database.loader import DataLoader
from session.manager import SessionManager
from utils.keyboards import get_next_keyboard, get_main_menu_keyboard
from handlers.game import send_question
import config

def register_callbacks(
    bot: telebot.TeleBot,
    data_loader: DataLoader,
    session_manager: SessionManager
):
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
    def handle_answer(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        user_answer = call.data[7:]  # Убираем 'answer_'
        
        # Проверяем сессию
        session = session_manager.get_session(user_id)
        if not session:
            bot.answer_callback_query(call.id, "Сессия устарела")
            bot.send_message(
                chat_id, 
                "📝 Начни сначала, нажав 'Начать' в меню.",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        employee = session['current_employee']
        
        # Определяем результат
        if user_answer == employee.short_name:
            result = f"✅ Абсолютно верно!"
        else:
            result = f"❌ Не угадал. Это был(а) *{employee.short_name}*."
        
        # Формируем информацию о сотруднике
        info_text = employee.format_info(result)
        
        # Удаляем клавиатуру с вариантами
        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except:
            pass
        
        # Отправляем информацию с кнопкой Далее
        bot.send_message(
            chat_id, 
            info_text, 
            parse_mode='Markdown',
            disable_web_page_preview=True,
            reply_markup=get_next_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "next")
    def handle_next(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # Удаляем клавиатуру
        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except:
            pass
        
        # Отправляем следующий вопрос
        send_question(bot, chat_id, user_id, data_loader, session_manager)