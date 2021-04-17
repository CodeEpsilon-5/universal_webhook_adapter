from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./sql_app.db"
    host_url: str = "http://127.0.0.1"
    max_adapters: int = 10
    clean_interval: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
