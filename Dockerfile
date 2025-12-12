FROM python:3.10-slim

# Оптимизация Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем uv — официальный способ работы с pyproject.toml
RUN pip install uv

WORKDIR /app

# Копируем только pyproject.toml для кеширования слоёв
COPY pyproject.toml ./

# Устанавливаем зависимости по pyproject.toml
RUN uv pip install --system --no-cache .

# Копируем весь проект
COPY . .

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
