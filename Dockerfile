FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY bot.py /app/bot.py
COPY migrate_sqlite_to_postgres.py /app/migrate_sqlite_to_postgres.py
COPY data/lang.yml /app/data/lang.yml
COPY data/markup_inline.py /app/data/markup_inline.py

RUN mkdir -p /app/logs

CMD ["python", "bot.py"]
