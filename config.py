import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    """Application configuration settings loaded from environment variables."""
    
    # Flask Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    
    # Database Settings
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Server Settings
    PORT = int(os.getenv("PORT", 5000))
