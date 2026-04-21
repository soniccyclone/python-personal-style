from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_path: Path = Path('bookmarks.db')
    host: str = '127.0.0.1'
    port: int = 8000
    log_level: str = 'INFO'

    model_config = SettingsConfigDict(env_prefix='BOOKMARKS_', env_file='.env', extra='ignore')
