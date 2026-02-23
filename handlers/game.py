import telebot
import random
import sys
import traceback
from utils.helpers import convert_drive_link_to_direct, download_file_from_url
from utils.keyboards import get_answer_keyboard, get_next_keyboard
from database.loader import DataLoader
from session.manager import SessionManager
import config

def send_question(
    bot: telebot.TeleBot,
    chat_id: int,
    user_id: int,
    data_loader: DataLoader,
    session_manager: SessionManager
):
    """Отправляет вопрос с фото и вариантами ответов"""
    
    print(f"📤 Отправляю вопрос для user_id: {user_id}")
    sys.stdout.flush()
    
    if data_loader.data is None or data_loader.data.empty:
        bot.send_message(chat_id, config.MESSAGES['data_loading'])
        return
    
    try:
        # Получаем предыдущего сотрудника для исключения
        session = session_manager.get_session(user_id)
        exclude_id = session.get('last_employee_id') if session else None
        
        # Выбираем случайного сотрудника
        employee = data_loader.get_random_employee(exclude_id)
        if not employee:
            employee = data_loader.get_random_employee()
        
        # Получаем все короткие имена для вариантов
        all_short_names = data_loader.data['short_name'].tolist()
        wrong_names = [name for name in all_short_names if name != employee.short_name]
        
        # Формируем варианты ответов
        if len(wrong_names) < 3:
            wrong_options = random.sample(wrong_names, len(wrong_names)) if wrong_names else []
            while len(wrong_options) < 3:
                wrong_options.append("Неизвестно")
        else:
            wrong_options = random.sample(wrong_names, 3)
        
        options = [employee.short_name] + wrong_options
        random.shuffle(options)
        
        # Сохраняем сессию
        session_manager.create_session(user_id, employee, options)
        
        # Отправляем фото с кнопками
        send_photo_with_buttons(bot, chat_id, employee, options)
        
    except Exception as e:
        print(f"❌ Ошибка в send_question: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        bot.send_message(chat_id, config.MESSAGES['error'])

def send_photo_with_buttons(
    bot: telebot.TeleBot,
    chat_id: int,
    employee,
    options: list
):
    """Отправляет фото с клавиатурой ответов"""
    
    try:
        direct_url = convert_drive_link_to_direct(employee.photo_url)
        print(f"📸 Конвертированная ссылка: {direct_url}")
        
        keyboard = get_answer_keyboard(options)
        bot.send_photo(
            chat_id, 
            direct_url, 
            caption="🔍 Кто это? 👆", 
            reply_markup=keyboard
        )
        
    except Exception as photo_error:
        print(f"❌ Ошибка отправки фото: {photo_error}")
        
        # Пробуем скачать и отправить
        try:
            download_url = direct_url.replace('export=view', 'export=download')
            img_data = download_file_from_url(download_url)
            
            if img_data:
                keyboard = get_answer_keyboard(options)
                bot.send_photo(
                    chat_id, 
                    img_data, 
                    caption="🔍 Кто это? 👆", 
                    reply_markup=keyboard
                )
                print("✅ Фото отправлено через скачивание")
            else:
                raise Exception("Не удалось скачать фото")
                
        except Exception as download_error:
            print(f"❌ Ошибка скачивания: {download_error}")
            error_msg = (
                "📸 Не удалось загрузить фото.\n"
                f"Это **{employee.full_name}**\n\n"
                "Возможные причины:\n"
                "• Файл требует входа в Google\n"
                "• Ссылка устарела\n"
                "• Файл был удален"
            )
            keyboard = get_answer_keyboard(options)
            bot.send_message(
                chat_id, 
                error_msg, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )