from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database – MySQL connection.
    # The '@' in the password is URL-encoded as '%40'.
    database_url: str = "mysql+pymysql://root:Vishnu%40123@localhost:3306/nsfw_copyright_db"

    # Machine learning models (Hugging Face hub ids).
    nsfw_model_id: str = "Falconsai/nsfw_image_detection"
    clip_model_id: str = "openai/clip-vit-base-patch32"

    # Thresholds.
    nsfw_threshold: float = 0.5
    duplicate_threshold: float = 0.92

    # GIF / animated image keyframe sampling.
    max_gif_frames: int = 16

    # CORS origins for the frontend dev server.
    cors_origins: str = "*"

    # If true, ML models are lazily loaded; set false to load eagerly at startup.
    lazy_load_models: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
