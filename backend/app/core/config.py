import os
from dotenv import load_dotenv

# Load .env file in development
load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Sales & Customer Analytics Platform"
    
    # Secrets
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_default_key_change_me_in_production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 Hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # File Storage
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data_store")
    MAX_FILE_SIZE_MB: int = 100

# Instantiate settings
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
