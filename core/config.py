from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "API Usuarios"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "cambia_esta_clave_secreta_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite:///./usuarios.db"

    model_config = {"env_file": ".env"}


settings = Settings()
