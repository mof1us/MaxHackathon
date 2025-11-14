FROM python:3.13
COPY requirements.txt .
COPY maxapi .


RUN apt-get update && apt-get install -y --no-install-recommends locales \
    && sed -i 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen ru_RU.UTF-8 \
    && update-locale LANG=ru_RU.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Переменные окружения по умолчанию
ENV LANG=ru_RU.UTF-8
ENV LC_ALL=ru_RU.UTF-8

RUN pip3 install --no-cache-dir -r requirements.txt
WORKDIR /bot
COPY . .
CMD ["python", "main.py"]