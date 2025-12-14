FROM python:3.10-slim

# Оптимизация Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем pip и fastapi dev CLI
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir fastapi[dev] uvicorn[standard]

WORKDIR /app

# Кешируем зависимости (если есть pyproject.toml/requirements.txt)
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Монтирование кода через volume будет в docker-compose
# COPY . .   <-- НЕ делаем копию кода, чтобы live-reload работал

# Healthcheck (FastAPI)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000))"

# FastAPI dev (новый CLI)
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
