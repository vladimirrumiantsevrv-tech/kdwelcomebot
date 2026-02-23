from typing import Dict, Optional, Any
from database.models import Employee

class SessionManager:
    """Управляет сессиями пользователей"""
    
    def __init__(self):
        self.sessions: Dict[int, Dict[str, Any]] = {}
    
    def create_session(self, user_id: int, employee: Employee, options: list):
        """Создает новую сессию"""
        self.sessions[user_id] = {
            'current_employee': employee,
            'last_employee_id': employee.id,
            'options': options,
            'correct_short_name': employee.short_name
        }
    
    def get_session(self, user_id: int) -> Optional[Dict]:
        """Возвращает сессию пользователя"""
        return self.sessions.get(user_id)
    
    def update_session(self, user_id: int, **kwargs):
        """Обновляет сессию пользователя"""
        if user_id in self.sessions:
            self.sessions[user_id].update(kwargs)
    
    def clear_session(self, user_id: int):
        """Очищает сессию"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def session_exists(self, user_id: int) -> bool:
        """Проверяет существование сессии"""
        return user_id in self.sessions