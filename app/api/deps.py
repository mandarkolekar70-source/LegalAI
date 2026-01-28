from functools import wraps
from flask import request, jsonify
import jwt
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"detail": "Token is missing!"}), 401

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            email = payload.get("sub")
            if not email:
                return jsonify({"detail": "Invalid token"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"detail": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"detail": "Invalid token"}), 401

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return jsonify({"detail": "User not found"}), 401
        finally:
            db.close()

        return f(user, *args, **kwargs)

    return decorated
