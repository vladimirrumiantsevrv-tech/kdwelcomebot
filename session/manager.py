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
        print(f"✅ Создана сессия для user {user_id}, stage=name, employee={employee.short_name}")
        print(f"📋 position_options: {position_options}")
    
    def get_session(self, user_id: int) -> Optional[Dict]:
        """Возвращает сессию пользователя"""
        session = self.sessions.get(user_id)
        if session:
            print(f"📊 Получена сессия для user {user_id}: stage={session.get('stage')}")
        else:
            print(f"❌ Сессия не найдена для user {user_id}")
        return session
    
    def update_session(self, user_id: int, **kwargs):
        """Обновляет сессию пользователя"""
        if user_id in self.sessions:
            self.sessions[user_id].update(kwargs)
            print(f"✅ Сессия обновлена для user {user_id}: {kwargs}")
    
    def update_stage(self, user_id: int, stage: str):
        """Обновляет этап игры"""
        if user_id in self.sessions:
            self.sessions[user_id]['stage'] = stage
            print(f"✅ Обновлен stage для user {user_id}: {stage}")
    
    def clear_session(self, user_id: int):
        """Очищает сессию"""
        if user_id in self.sessions:
            print(f"🗑 Очищаем сессию для user {user_id}")
            del self.sessions[user_id]
    
    def session_exists(self, user_id: int) -> bool:
        """Проверяет существование сессии"""
        return user_id in self.sessions