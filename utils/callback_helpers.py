import hashlib
import json
from typing import Dict, Tuple, Optional

# Хранилище соответствий между короткими ключами и реальными значениями
_callback_storage: Dict[str, Tuple[str, str]] = {}  # key -> (type, value)

def create_callback_data(prefix: str, value: str) -> str:
    """
    Создает безопасный callback_data из длинного значения
    prefix: 'answer' или 'position'
    value: оригинальное значение (имя или должность)
    """
    # Создаем короткий хеш от значения
    hash_obj = hashlib.md5(value.encode())
    short_key = hash_obj.hexdigest()[:8]  # Берем первые 8 символов хеша
    
    # Сохраняем соответствие
    _callback_storage[short_key] = (prefix, value)
    
    # Возвращаем короткий callback_data
    return f"{prefix}_{short_key}"

def parse_callback_data(callback_data: str) -> Optional[Tuple[str, str]]:
    """
    Парсит callback_data и возвращает (тип, оригинальное значение)
    """
    try:
        prefix, short_key = callback_data.split('_', 1)
        if short_key in _callback_storage:
            stored_prefix, original_value = _callback_storage[short_key]
            if stored_prefix == prefix:
                return prefix, original_value
    except:
        pass
    return None

def cleanup_old_keys():
    """Очищает старые ключи (можно вызывать периодически)"""
    # Простая реализация - очищаем всё (для продакшена нужно лучше)
    _callback_storage.clear()