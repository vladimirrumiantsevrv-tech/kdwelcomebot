FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    gfortran \\
    libopenblas-dev \\
    libatlas-base-dev \\
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .

# Устанавливаем numpy сначала, потом pandas
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \\
    pip install --no-cache-dir numpy==1.24.3 && \\
    pip install --no-cache-dir pandas==1.5.3

# Устанавливаем остальные зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Запускаем бота
CMD ["python", "main.py"]
