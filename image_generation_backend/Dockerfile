# База: чистый Ubuntu LTS
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Базовые пакеты + Python + утилиты для установки ключей репозиториев
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    gnupg \
    python3 \
    python3-pip \
    python3-venv \
    # полезные шрифты, чтобы Chrome корректно рендерил страницы
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

# Установка Google Chrome (stable) из официального репозитория Google
RUN mkdir -p /etc/apt/keyrings \
 && wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /etc/apt/keyrings/google-linux.gpg \
 && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# (Необязательно) Установите зависимости вашего проекта, если есть:
 COPY requirements.txt .
 RUN pip3 install --no-cache-dir -r requirements.txt

# Копируйте код, если нужно:
 COPY . .



# По умолчанию открываем интерактивный Python
CMD ["python3", "main.py"]
