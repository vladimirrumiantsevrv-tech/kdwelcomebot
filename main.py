#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import time
import sys
import traceback
from database.loader import DataLoader
from session.manager import SessionManager
from handlers import commands, menu, callbacks
import config

print("=" * 60)
print("🚀 ЗАПУСК БОТА")
print("=" * 60)
sys.stdout.flush()

def main():
    # Инициализация компонентов
    bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
    data_loader = DataLoader()
    session_manager = SessionManager()
    
    # Загрузка данных при старте
    try:
        print("📥 Загружаю данные...")
        if data_loader.load_data():
            print(f"✅ Данные загружены: {len(data_loader.data)} записей")
        else:
            print("⚠️ Не удалось загрузить данные")
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        traceback.print_exc()
    
    # Регистрация обработчиков
    commands.register_commands(bot, data_loader)
    menu.register_menu_handlers(bot, data_loader, session_manager)
    callbacks.register_callbacks(bot, data_loader, session_manager)
    
    print("\n" + "=" * 60)
    print("🚀 Бот запущен и готов к работе!")
    print("📊 Команда /status для проверки состояния")
    print("📝 Команда /reload для ручного обновления")
    print("=" * 60 + "\n")
    sys.stdout.flush()
    
    # Запуск бота
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"⚠️ Ошибка соединения: {e}. Переподключение через 5 секунд...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == '__main__':
    main()