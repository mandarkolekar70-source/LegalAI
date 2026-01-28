from flask import Blueprint, request, jsonify
from app.api.deps import token_required
from app.models.user import User
from app.agents.classifier import CaseClassifier
from app.agents.rag import LegalReasoningAgent
from app.vector_store.faiss_store import VectorStore
from app.etl.extractor import extract_text_from_pdf
from app.models.case import CaseRecord
from app.core.database import SessionLocal

import os
import uuid

analysis_bp = Blueprint("analysis", __name__)

classifier = CaseClassifier()
vector_store = VectorStore()
rag_agent = LegalReasoningAgent(vector_store)

@analysis_bp.route("/analyze", methods=["POST"])
@token_required
def analyze_case(current_user: User):

    description = request.form.get("description")
    files = request.files.getlist("files")

    if not description:
        return jsonify({"error": "Description is required"}), 400

    file_texts = ""
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        if file and file.filename.endswith(".pdf"):
            file_id = str(uuid.uuid4())
            file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
            file.save(file_path)

            try:
                file_texts += "\n" + extract_text_from_pdf(file_path)
            except Exception as e:
                print("PDF extraction error:", e)

    full_text = description + "\n" + file_texts

    classification_scores = classifier.classify(full_text)
    confidence = classifier.calculate_confidence(classification_scores)

    labels = list(classification_scores.keys())
    primary = labels[0]
    secondary = None

    if len(labels) > 1 and classification_scores[labels[1]] >= classification_scores[labels[0]] * 0.75:
        secondary = labels[1]

    analysis_result = rag_agent.analyze_case_sync(
        full_text, primary, secondary
    )

    db = SessionLocal()
    try:
        new_case = CaseRecord(
            user_id=current_user.id,
            description=description,
            case_type=primary,
            classification_json=classification_scores,
            analysis_json=analysis_result
        )

        db.add(new_case)
        db.commit()
        db.refresh(new_case)

        return jsonify({
            "id": new_case.id,
            "classification": {
                "primary": primary,
                "secondary": f"{secondary} (subject to proof of intent)" if secondary else None,
                "confidence": f"{confidence}%"
            },
            "analysis": analysis_result
        })

    finally:
        db.close()
