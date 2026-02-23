import pandas as pd
import io
import sys
from typing import Optional, List
from utils.helpers import get_direct_download_link, download_file_from_url, extract_first_last_name
import config

class DataLoader:
    """Загружает и обрабатывает данные из Google Drive"""
    
    def __init__(self):
        self.data = None
        self.allowed_users = []
        self.last_update_time = 0
    
    def load_data(self) -> bool:
        """Загружает данные из файла"""
        print("\n" + "=" * 60)
        print("🚀 НАЧАЛО ЗАГРУЗКИ ДАННЫХ")
        print("=" * 60)
        sys.stdout.flush()
        
        try:
            # Получаем прямую ссылку для скачивания
            download_url = get_direct_download_link(config.GOOGLE_FILE_URL)
            print(f"📌 Ссылка для скачивания: {download_url}")
            
            # Скачиваем файл
            file_content = download_file_from_url(download_url)
            if not file_content:
                return False
            
            # Пробуем прочитать файл в разных форматах
            new_data = self._read_file(file_content)
            if new_data is None:
                return False
            
            # Обрабатываем данные
            new_data = self._process_dataframe(new_data)
            if new_data is None:
                return False
            
            # Сохраняем данные
            self.data = new_data
            self.last_update_time = pd.Timestamp.now()
            
            print(f"\n✅ УСПЕХ! Данные загружены: {len(self.data)} записей")
            print("=" * 60)
            sys.stdout.flush()
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return False
    
    def _read_file(self, file_content: bytes) -> Optional[pd.DataFrame]:
        """Пытается прочитать файл в разных форматах"""
        # Пробуем CSV с запятой
        try:
            csv_data = io.StringIO(file_content.decode('utf-8'))
            df = pd.read_csv(csv_data, delimiter=',')
            print("✅ Прочитан как CSV с разделителем ','")
            return df
        except:
            pass
        
        # Пробуем CSV с точкой с запятой
        try:
            csv_data = io.StringIO(file_content.decode('utf-8'))
            df = pd.read_csv(csv_data, delimiter=';')
            print("✅ Прочитан как CSV с разделителем ';'")
            return df
        except:
            pass
        
        # Пробуем Excel
        try:
            file_bytes = io.BytesIO(file_content)
            df = pd.read_excel(file_bytes)
            print("✅ Прочитан как Excel")
            return df
        except Exception as e:
            print(f"❌ Не удалось прочитать файл: {e}")
            return None
    
    def _process_dataframe(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Обрабатывает DataFrame: переименовывает колонки, фильтрует"""
        
        # Очищаем названия колонок
        df.columns = df.columns.str.strip()
        
        # Переименовываем колонки согласно конфигурации
        rename_dict = {}
        for key, col_name in config.COLUMN_NAMES.items():
            if col_name in df.columns:
                rename_dict[col_name] = key
        
        if rename_dict:
            df = df.rename(columns=rename_dict)
        
        # ОТЛАДКА: выводим все колонки после переименования
        print(f"📌 Колонки после переименования: {list(df.columns)}")
        if 'letter' in df.columns:
            print(f"📌 Найдена колонка с letter, примеры: {df['letter'].head(3).tolist()}")
        
        # Проверяем наличие обязательных колонок
        required = ['name', 'telegram', 'photo']
        missing = [col for col in required if col not in df.columns]
        if missing:
            print(f"❌ Отсутствуют обязательные колонки: {missing}")
            return None
        
        # Фильтруем строки без фото и имени
        df = df[df['photo'].notna() & df['name'].notna()]
        
        # Добавляем сокращенное имя
        df['short_name'] = df['name'].apply(extract_first_last_name)
        
        # Формируем список разрешенных пользователей
        self._build_allowed_users(df)
        
        return df
    
    def _build_allowed_users(self, df: pd.DataFrame):
        """Формирует список разрешенных пользователей из колонки telegram"""
        raw_telegrams = df['telegram'].dropna()
        self.allowed_users = []
        
        for user in raw_telegrams:
            if pd.notna(user) and str(user).strip():
                clean_user = str(user).lower().replace('@', '').strip()
                if clean_user:
                    self.allowed_users.append(clean_user)
        
        print(f"📌 Разрешено пользователей: {len(self.allowed_users)}")
    
    def get_random_employee(self, exclude_id: Optional[int] = None):
        """Возвращает случайного сотрудника, исключая указанный ID"""
        from database.models import Employee
        
        if self.data is None or self.data.empty:
            return None
        
        if exclude_id is not None:
            available = self.data.drop(exclude_id, errors='ignore')
            if len(available) == 0:
                available = self.data
        else:
            available = self.data
        
        row = available.sample().iloc[0]
        return Employee.from_dataframe_row(row)
    
    def get_employee_by_id(self, employee_id: int):
        """Возвращает сотрудника по ID"""
        from database.models import Employee
        
        if self.data is None or employee_id not in self.data.index:
            return None
        
        row = self.data.loc[employee_id]
        return Employee.from_dataframe_row(row)
    
    def is_user_allowed(self, username: str) -> bool:
        """Проверяет, разрешен ли пользователь"""
        if not username:
            return False
        return username.lower() in self.allowed_users