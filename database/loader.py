import pandas as pd
import sys
from typing import Optional, List, Set
from utils.helpers import extract_first_last_name
from utils.google_drive import GoogleDriveClient
import config

class DataLoader:
    """Загружает и обрабатывает данные из Google Drive через сервисный аккаунт"""
    
    def __init__(self):
        self.data = None
        self.allowed_users = []
        self.last_update_time = 0
        self.drive_client = None
        self._init_drive_client()
    
    def _init_drive_client(self):
        """Инициализирует клиент Google Drive"""
        try:
            if config.GOOGLE_CREDENTIALS_JSON:
                self.drive_client = GoogleDriveClient(
                    credentials_json=config.GOOGLE_CREDENTIALS_JSON
                )
            else:
                self.drive_client = GoogleDriveClient(
                    credentials_file=config.GOOGLE_CREDENTIALS_FILE
                )
            print("✅ Google Drive клиент инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации Google Drive: {e}")
            self.drive_client = None
    
    def load_data(self) -> bool:
        """Загружает данные из файла через сервисный аккаунт"""
        print("\n" + "=" * 60)
        print("🚀 НАЧАЛО ЗАГРУЗКИ ДАННЫХ (через сервисный аккаунт)")
        print("=" * 60)
        sys.stdout.flush()
        
        if not self.drive_client:
            print("❌ Google Drive клиент не инициализирован")
            return False
        
        try:
            # Получаем ID файла из URL
            file_id = self.drive_client.extract_file_id_from_url(config.GOOGLE_FILE_URL)
            if not file_id:
                print(f"❌ Не удалось извлечь ID файла из URL: {config.GOOGLE_FILE_URL}")
                return False
            
            print(f"📌 ID файла: {file_id}")
            
            # Получаем метаданные для проверки доступа
            metadata = self.drive_client.get_file_metadata(file_id)
            if metadata:
                print(f"📌 Файл: {metadata.get('name')} ({metadata.get('mimeType')})")
                print(f"📌 Изменен: {metadata.get('modifiedTime')}")
            
            # Скачиваем и читаем данные
            new_data = self.drive_client.download_as_dataframe(file_id)
            if new_data is None:
                print("❌ Не удалось скачать/прочитать файл")
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
            import traceback
            traceback.print_exc()
            return False
    
    def _process_dataframe(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Обрабатывает DataFrame: переименовывает колонки, фильтрует"""
        # [остальной код остается без изменений]
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
    
    def get_random_employee(self, exclude_ids: Optional[Set[int]] = None):
        """Возвращает случайного сотрудника, исключая указанные ID (уже угаданных)"""
        from database.models import Employee
        
        if self.data is None or self.data.empty:
            return None
        
        if exclude_ids and len(exclude_ids) > 0:
            available = self.data[~self.data.index.isin(exclude_ids)]
            if len(available) == 0:
                return None
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