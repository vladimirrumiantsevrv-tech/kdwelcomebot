import requests
import pandas as pd
import io
import sys
from typing import Optional, Tuple

def get_direct_download_link(drive_url: str) -> str:
    """
    Преобразует обычную ссылку на Google Диск в прямую ссылку для скачивания файла
    """
    try:
        if 'drive.google.com' not in drive_url:
            return drive_url
        
        if '/file/d/' in drive_url:
            file_id = drive_url.split('/file/d/')[1].split('/')[0]
            return f'https://drive.google.com/uc?export=download&id={file_id}'
        elif 'open?id=' in drive_url:
            file_id = drive_url.split('open?id=')[1].split('&')[0]
            return f'https://drive.google.com/uc?export=download&id={file_id}'
        else:
            return drive_url
    except Exception as e:
        print(f"❌ Ошибка при обработке ссылки: {e}")
        return drive_url

def convert_drive_link_to_direct(photo_link: str) -> str:
    """
    Преобразует ссылку на страницу Google Диска в прямую ссылку на изображение
    """
    try:
        if 'drive.google.com' not in photo_link:
            return photo_link
        
        if '/file/d/' in photo_link:
            file_id = photo_link.split('/file/d/')[1].split('/')[0]
        elif 'open?id=' in photo_link:
            file_id = photo_link.split('open?id=')[1].split('&')[0]
        else:
            return photo_link
        
        return f'https://drive.google.com/uc?export=view&id={file_id}'
    except Exception as e:
        print(f"❌ Ошибка конвертации ссылки на фото: {e}")
        return photo_link

def extract_first_last_name(full_name: str) -> str:
    """
    Извлекает только имя и фамилию из полного ФИО
    Берет первые два слова до второго пробела
    """
    try:
        if pd.isna(full_name) or not str(full_name).strip():
            return "Неизвестно"
        
        parts = str(full_name).strip().split()
        
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
        elif len(parts) == 1:
            return parts[0]
        else:
            return "Неизвестно"
    except Exception as e:
        print(f"❌ Ошибка при извлечении имени/фамилии: {e}")
        return str(full_name)

def download_file_from_url(url: str) -> Optional[bytes]:
    """Скачивает файл по URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"❌ Ошибка загрузки: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка при скачивании: {e}")
        return None