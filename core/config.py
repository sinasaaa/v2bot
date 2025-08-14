# ===== IMPORTS & DEPENDENCIES =====
from pydantic_settings import BaseSettings

# ===== CONFIGURATION & CONSTANTS =====
class Settings(BaseSettings):
    # Telegram Settings
    TELEGRAM_BOT_TOKEN: str
    
    # The main admin's Telegram User ID. Get it from @userinfobot
    ADMIN_USER_ID: int

    # Webhook Settings
    # This should be your server's public URL, e.g., https://yourdomain.com
    WEBHOOK_URL: str
    
    # Database Settings (PostgreSQL)
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost/v2raybot_db"

    # Load settings from a .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a single instance of the settings to be used throughout the application
settings = Settings()
