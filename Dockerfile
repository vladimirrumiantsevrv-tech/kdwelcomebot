FROM python:3.11-slim

WORKDIR /app

# Устанавливаем только build-essential (включает всё необходимое)
RUN apt-get update && apt-get install -y build-essential libopenblas-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Устанавливаем все зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pandas==1.5.3 && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]