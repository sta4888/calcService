FROM python:3.10-slim

# Оптимизация Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Кешируем зависимости
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

# Копируем проект
COPY . .

# Healthcheck (FastAPI)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000))"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
