from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Добавляем описание
    app_title: str
    description: str
    version: str

    # Добавляем недостающие параметры для Postgres
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    #Добавляем токены доступа
    API_TOKEN: str
    LOCAL_API_URL: str
    TOKEN_API_SANDBOX: str
    TOKEN_API_LIVE: str
    TELEGRAM_BOT_TOKEN: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()