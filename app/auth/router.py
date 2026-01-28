from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta

from app.core.database import SessionLocal
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)
from app.core.config import settings
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

# ---------- SIGNUP ----------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"detail": "Invalid JSON"}), 400

    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not email or not password:
        return jsonify({"detail": "Email and password required"}), 400

    db: Session = SessionLocal()
    try:
        existing = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing:
            return jsonify({"detail": "Email already registered"}), 400

        user = User(
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return jsonify({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }), 201

    finally:
        db.close()


# ---------- LOGIN ----------
@auth_bp.route("/login", methods=["POST"])
def login():
    if request.is_json:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

    db: Session = SessionLocal()
    try:
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            return jsonify({"detail": "Invalid credentials"}), 401

        token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        return jsonify({
            "access_token": token,
            "token_type": "bearer"
        })

    finally:
        db.close()
