from typing import Dict, Optional, Any, List
from database.models import Employee

class SessionManager:
    """Управляет сессиями пользователей"""
    
    def __init__(self):
        self.sessions: Dict[int, Dict[str, Any]] = {}
    
    def create_session(
        self, 
        user_id: int, 
        employee: Employee, 
        name_options: List[str],
        position_options: List[str] = None
    ):
        """Создает новую сессию с поддержкой двух этапов"""
        self.sessions[user_id] = {
            'current_employee': employee,
            'last_employee_id': employee.id,
            'name_options': name_options,
            'position_options': position_options or [],
            'correct_short_name': employee.short_name,
            'correct_position': employee.position,
            'stage': 'name'  # 'name' или 'position'
        }
    
    def get_session(self, user_id: int) -> Optional[Dict]:
        """Возвращает сессию пользователя"""
        return self.sessions.get(user_id)
    
    def update_session(self, user_id: int, **kwargs):
        """Обновляет сессию пользователя"""
        if user_id in self.sessions:
            self.sessions[user_id].update(kwargs)
    
    def update_stage(self, user_id: int, stage: str):
        """Обновляет этап игры"""
        if user_id in self.sessions:
            self.sessions[user_id]['stage'] = stage
    
    def clear_session(self, user_id: int):
        """Очищает сессию"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def session_exists(self, user_id: int) -> bool:
        """Проверяет существование сессии"""
        return user_id in self.sessions