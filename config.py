import os
from dotenv import load_dotenv
import json

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токены и URL
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_FILE_URL = os.getenv("GOOGLE_FILE_URL")

# Учетные данные для Google Drive сервисного аккаунта
# Можно хранить как JSON строку в .env или как отдельный файл
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# Настройки
UPDATE_INTERVAL = 300  # 5 минут
DEBUG = True

# Названия колонок в таблице
COLUMN_NAMES = {
    'name': 'ФИО',
    'position': 'Должность',
    'department': 'Отдел',
    'telegram': 'Telegram',
    'photo': 'Фото',
    'letter': 'Велкомы'
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
if not GOOGLE_CREDENTIALS_JSON and not os.path.exists(GOOGLE_CREDENTIALS_FILE):
    raise ValueError("❌ Нет учетных данных Google Drive. Укажите GOOGLE_CREDENTIALS_JSON или создайте credentials.json")