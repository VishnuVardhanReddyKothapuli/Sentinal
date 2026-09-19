from functools import lru_cache
from pathlib import Path
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env', override=False)
load_dotenv(Path(__file__).resolve().parents[2] / '.env', override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=('../.env', '.env'), extra='ignore')

    database_url: str = 'sqlite:///./data/sentinel.db'
    jwt_secret: str = ''
    jwt_expire_minutes: int = 480
    data_dir: Path = Path('data')
    upload_dir: Path | None = None
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    max_upload_mb: int = 50
    inference_concurrency: int = 1
    auto_create_tables: bool = True
    environment: str = 'development'

    def signing_key(self) -> str:
        if self.jwt_secret:
            if len(self.jwt_secret) < 32:
                raise ValueError('JWT_SECRET must contain at least 32 characters')
            return self.jwt_secret
        if self.environment != 'development':
            raise ValueError('Set JWT_SECRET in production')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        key_path = self.data_dir / '.jwt-secret'
        try:
            with key_path.open('x', encoding='utf-8') as handle:
                handle.write(secrets.token_urlsafe(48))
            key_path.chmod(0o600)
        except FileExistsError:
            pass
        key = key_path.read_text(encoding='utf-8').strip()
        if len(key) < 32:
            raise ValueError('Stored development JWT secret is invalid; set JWT_SECRET')
        return key


@lru_cache
def get_settings() -> Settings:
    return Settings()
