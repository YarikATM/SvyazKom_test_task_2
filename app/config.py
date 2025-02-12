from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Config(BaseSettings):

    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_PORT: str

    API_URL: str
    API_USER: str
    API_PASSWORD: SecretStr

    SCHEDULER_INTERVAL: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


