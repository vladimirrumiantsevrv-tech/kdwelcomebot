import os
import json
import io
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd

class GoogleDriveClient:
    """Клиент для безопасной работы с Google Drive через сервисный аккаунт"""
    
    def __init__(self, credentials_json: str = None, credentials_file: str = None):
        """
        Инициализация клиента Google Drive
        Можно передать либо JSON строку с credentials, либо путь к файлу
        """
        self.service = self._authenticate(credentials_json, credentials_file)
    
    def _authenticate(self, credentials_json: str = None, credentials_file: str = None):
        """Аутентификация через сервисный аккаунт"""
        try:
            if credentials_json:
                # Загружаем из переменной окружения (JSON строка)
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
            elif credentials_file and os.path.exists(credentials_file):
                # Загружаем из файла
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
            else:
                raise ValueError("Не указаны учетные данные для Google Drive")
            
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"❌ Ошибка аутентификации Google Drive: {e}")
            raise
    
    def extract_file_id_from_url(self, url: str) -> Optional[str]:
        """Извлекает ID файла из ссылки Google Drive"""
        try:
            if '/file/d/' in url:
                return url.split('/file/d/')[1].split('/')[0]
            elif 'open?id=' in url:
                return url.split('open?id=')[1].split('&')[0]
            elif 'id=' in url:
                return url.split('id=')[1].split('&')[0]
            return None
        except Exception as e:
            print(f"❌ Ошибка извлечения ID файла: {e}")
            return None
    
    def download_file_as_bytes(self, file_id: str) -> Optional[bytes]:
        """Скачивает файл по ID и возвращает как bytes"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_bytes = io.BytesIO()
            downloader = MediaIoBaseDownload(file_bytes, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"📥 Загрузка: {int(status.progress() * 100)}%")
            
            file_bytes.seek(0)
            return file_bytes.getvalue()
            
        except Exception as e:
            print(f"❌ Ошибка скачивания файла: {e}")
            return None
    
    def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """Получает метаданные файла"""
        try:
            return self.service.files().get(
                fileId=file_id, 
                fields='name, mimeType, size, modifiedTime'
            ).execute()
        except Exception as e:
            print(f"❌ Ошибка получения метаданных: {e}")
            return None
    
    def download_as_dataframe(self, file_id: str) -> Optional[pd.DataFrame]:
        """Скачивает файл и пытается преобразовать в DataFrame"""
        file_bytes = self.download_file_as_bytes(file_id)
        if not file_bytes:
            return None
        
        # Пробуем прочитать как CSV или Excel
        try:
            # Пробуем CSV
            csv_data = io.StringIO(file_bytes.decode('utf-8'))
            return pd.read_csv(csv_data)
        except:
            try:
                # Пробуем CSV с другим разделителем
                csv_data = io.StringIO(file_bytes.decode('utf-8'))
                return pd.read_csv(csv_data, delimiter=';')
            except:
                try:
                    # Пробуем Excel
                    file_io = io.BytesIO(file_bytes)
                    return pd.read_excel(file_io)
                except Exception as e:
                    print(f"❌ Не удалось прочитать файл как таблицу: {e}")
                    return None