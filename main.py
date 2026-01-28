from flask import Flask, render_template
from flask_cors import CORS
from models.ipc_matcher import IPCMatcher

from app.core.database import Base, engine
from app.auth.router import auth_bp
from app.api.analysis import analysis_bp
from app.api.history import history_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(analysis_bp, url_prefix="/api")
app.register_blueprint(history_bp, url_prefix="/api/history")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
