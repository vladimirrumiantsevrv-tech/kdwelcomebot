FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости одной строкой
RUN apt-get update && apt-get install -y gcc g++ gfortran libopenblas-dev libatlas-base-dev && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .

# Устанавливаем все зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pandas && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Запускаем бота
CMD ["python", "main.py"]