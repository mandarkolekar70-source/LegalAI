class Settings:
    DATABASE_URL = "sqlite:///./legalai.db"
    SECRET_KEY = "super-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    ALGORITHM = "HS256"

settings = Settings()
