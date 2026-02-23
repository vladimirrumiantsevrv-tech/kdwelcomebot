from dataclasses import dataclass
from typing import Optional
import pandas as pd
from utils.helpers import extract_first_last_name

@dataclass
class Employee:
    """Модель сотрудника"""
    id: int
    full_name: str
    short_name: str
    position: str
    department: str
    telegram: str
    photo_url: str
    letter_url: Optional[str] = None
    
    @classmethod
    def from_dataframe_row(cls, row: pd.Series):
        """Создает объект из строки DataFrame"""
        full_name = row.get('name', '')
        
        return cls(
            id=row.name,
            full_name=full_name,
            short_name=row.get('short_name', extract_first_last_name(full_name)),
            position=row.get('position', 'Не указана'),
            department=row.get('department', 'Не указан'),
            telegram=row.get('telegram', ''),
            photo_url=row.get('photo', ''),
            letter_url=row.get('letter', '') if 'letter' in row else None
        )
    
    def format_info(self, with_result: Optional[str] = None) -> str:
        """Форматирует информацию о сотруднике для вывода"""
        info = ""
        
        if with_result:
            info += f"{with_result}\n\n"
        
        info += f"👤 *{self.short_name}*\n"
        info += f"📋 *Должность:* {self.position}\n"
        info += f"🏢 *Отдел:* {self.department}\n\n"
        
        if self.letter_url and pd.notna(self.letter_url) and str(self.letter_url).strip():
            info += f"📄 *Welcome-леттер:* [Прочитать]({self.letter_url})"
        else:
            info += "📄 *Welcome-леттер:* Не найден"
        
        return info