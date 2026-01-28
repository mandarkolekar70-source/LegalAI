from flask import Blueprint, jsonify

history_bp = Blueprint("history", __name__)

@history_bp.route("/", methods=["GET"])
def history():
    return jsonify([
        {"case": "Cheque Bounce", "date": "2025-01-10"},
        {"case": "Property Dispute", "date": "2025-01-15"}
    ])
