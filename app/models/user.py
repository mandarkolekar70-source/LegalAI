from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    profile_image = Column(String, nullable=True)
