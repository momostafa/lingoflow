# language_practice/src/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically calculate the global workspace root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "LingoFlow"
    
    # Store global base reference to use inside main application hooks
    BASE_DIR: Path = BASE_DIR
    
    # Absolute path resolutions targeted directly to nested folders
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/language_practice/data/practice.db"
    AUDIO_DIR: Path = BASE_DIR / "language_practice" / "static" / "audio"
    STATIC_DIR: Path = BASE_DIR / "language_practice" / "static"
    
    AI_PROVIDER: str = "local"  
    LOCAL_LLM_URL: str = "http://localhost:11434/v1"
    OPENAI_API_KEY: str = "mock-key"
    LLM_MODEL: str = "llama3.1:8b"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

settings = Settings()

# Bootstrap directory paths safely on boot
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
