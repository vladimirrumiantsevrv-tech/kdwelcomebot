import telebot
import random
import sys
import traceback
from utils.helpers import convert_drive_link_to_direct, download_file_from_url
from utils.keyboards import get_answer_keyboard, get_position_keyboard
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
    """Отправляет вопрос с фото и вариантами ответов (первый этап - угадать имя)"""
    
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
        
        # Формируем варианты ответов для имени
        if len(wrong_names) < 3:
            wrong_options = random.sample(wrong_names, len(wrong_names)) if wrong_names else []
            while len(wrong_options) < 3:
                wrong_options.append("Неизвестно")
        else:
            wrong_options = random.sample(wrong_names, 3)
        
        name_options = [employee.short_name] + wrong_options
        random.shuffle(name_options)
        
        # Получаем все должности для вариантов (второй этап)
        all_positions = data_loader.data['position'].dropna().unique().tolist()
        all_positions = [p for p in all_positions if p and str(p).strip() and p != employee.position]
        
        # Формируем варианты должностей
        if len(all_positions) < 3:
            position_options = random.sample(all_positions, len(all_positions)) if all_positions else []
            while len(position_options) < 3:
                position_options.append("Другая должность")
        else:
            position_options = random.sample(all_positions, 3)
        
        position_options = [employee.position] + position_options
        random.shuffle(position_options)
        
        # Сохраняем сессию с полной информацией
        session_manager.create_session(
            user_id, 
            employee, 
            name_options,
            position_options=position_options
        )
        
        # Отправляем фото с кнопками для имени
        send_photo_with_buttons(bot, chat_id, employee, name_options)
        
    except Exception as e:
        print(f"❌ Ошибка в send_question: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        bot.send_message(chat_id, config.MESSAGES['error'])

def send_position_question(
    bot: telebot.TeleBot,
    chat_id: int,
    user_id: int,
    session_manager: SessionManager,
    previous_result: str
):
    """Отправляет вопрос с вариантами должностей (второй этап)"""
    
    session = session_manager.get_session(user_id)
    if not session:
        bot.send_message(chat_id, config.MESSAGES['no_session'])
        return
    
    employee = session['current_employee']
    position_options = session.get('position_options', [])
    
    # Обновляем этап в сессии
    session_manager.update_stage(user_id, 'position')
    
    # Отправляем сообщение с результатом первого этапа и вопросом о должности
    message_text = f"{previous_result}\n\n{config.MESSAGES['ask_position']}"
    
    keyboard = get_position_keyboard(position_options)
    bot.send_message(
        chat_id,
        message_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

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