import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (для локальной разработки)
load_dotenv()

# Токены и URL
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_FILE_URL = os.getenv("GOOGLE_FILE_URL")

# Настройки
UPDATE_INTERVAL = 300  # 5 минут
DEBUG = True

# Названия колонок в таблице (настройте под свой файл)
COLUMN_NAMES = {
    'name': 'ФИО',           # Колонка с ФИО
    'position': 'Должность',  # Колонка с должностью
    'department': 'Отдел',    # Колонка с отделом
    'telegram': 'Telegram',   # Колонка с Telegram
    'photo': 'Фото',          # Колонка с фото
    'letter': 'Велкомы' # Колонка с welcome-леттером
}

# Тексты сообщений
MESSAGES = {
    'welcome': "👋 Привет! Давай проверим, насколько хорошо ты знаешь команду.",
    'no_session': "Нет активной сессии. Начните новую игру с кнопки 'Начать'.",
    'error': "❌ Ошибка при формировании вопроса. Попробуйте еще раз.",
    'access_denied': "❌ Извините, у вас нет доступа.",
    'no_username': "❌ У вас не установлен username. Установите его в настройках Telegram.",
    'data_loading': "⏳ Данные не загружены. Пожалуйста, подождите...",
    'data_empty': "⏳ Данные загружены, но таблица пуста.",
    'reload_success': "✅ Данные успешно обновлены! Загружено {count} записей.",
    'reload_error': "❌ Ошибка при обновлении данных."
}

# Кнопки меню
MENU_BUTTONS = {
    'start': "🚀 Начать",
    'continue': "⏯ Продолжить"
}

# Проверка наличия обязательных переменных
if not TELEGRAM_TOKEN:
    raise ValueError("❌ Нет переменной окружения TELEGRAM_BOT_TOKEN")
if not GOOGLE_FILE_URL:
    raise ValueError("❌ Нет переменной окружения GOOGLE_FILE_URL")