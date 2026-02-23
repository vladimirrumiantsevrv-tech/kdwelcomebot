import telebot
from database.loader import DataLoader
from session.manager import SessionManager
from utils.keyboards import get_next_keyboard, get_main_menu_keyboard
from handlers.game import send_position_question, send_question
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
        
        # Определяем результат для имени
        if user_answer == employee.short_name:
            result = f"✅ Абсолютно верно! Это *{employee.short_name}*."
        else:
            result = f"❌ Не угадал. Это был(а) *{employee.short_name}*."
        
        # Удаляем клавиатуру с вариантами имени
        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except:
            pass
        
        # Переходим ко второму этапу - угадывание должности
        send_position_question(bot, chat_id, user_id, session_manager, result)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('position_'))
    def handle_position_answer(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        user_answer = call.data[9:]  # Убираем 'position_'
        
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
        
        # Определяем результат для должности
        if user_answer == employee.position:
            position_result = config.MESSAGES['position_correct']
        else:
            position_result = config.MESSAGES['position_wrong'].format(position=employee.position)
        
        # Удаляем клавиатуру с вариантами должности
        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except:
            pass
        
        # Получаем текст предыдущего сообщения (результат первого этапа)
        previous_text = call.message.text
        # Убираем вопрос о должности, оставляем только результат первого этапа
        if config.MESSAGES['ask_position'] in previous_text:
            previous_text = previous_text.replace(f"\n\n{config.MESSAGES['ask_position']}", "")
        
        # Формируем финальную информацию о сотруднике
        final_result = f"{previous_text}\n\n{position_result}"
        info_text = employee.format_info(final_result)
        
        # Отправляем информацию с кнопкой Далее
        bot.send_message(
            chat_id, 
            info_text, 
            parse_mode='Markdown',
            disable_web_page_preview=True,
            reply_markup=get_next_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "next")
    @bot.callback_query_handler(func=lambda call: call.data == "next")
    def handle_next(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
    
        print(f"➡️ Next pressed for user {user_id}")  # Отладка
    
        # Удаляем клавиатуру
        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except:
            pass
    
        # ВАЖНО: Очищаем старую сессию перед созданием новой
        session_manager.clear_session(user_id)
    
        # Отправляем следующий вопрос
        send_question(bot, chat_id, user_id, data_loader, session_manager)