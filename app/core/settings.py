from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str
    alembic_database_url: str

    # Postgres (если нужны отдельно)
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # RabbitMQ
    rabbitmq_url: str
    rabbitmq_user: str
    rabbitmq_pass: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",  # ← пусть будет строго
    )


settings = Settings()
