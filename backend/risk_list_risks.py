### ✅ FINAL risk_list_risks.py (Flask backend)
from flask import Blueprint, jsonify, request, send_from_directory
import os

risk_list_bp = Blueprint('risk_list', __name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved_files', 'risk'))
CSV_DIR = os.path.join(BASE_DIR, 'csvs')
IMG_DIR = os.path.join(BASE_DIR, 'images')

@risk_list_bp.route('/api/list_risks', methods=['GET'])
def list_risks():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    risk_reports = []

    # Locate the session's CSV
    csv_files = [f for f in os.listdir(CSV_DIR) if f.startswith(session_id) and f.endswith('.csv')]
    if not csv_files:
        return jsonify([])

    csv_filename = csv_files[0]

    # Locate all saved PNG images for this session
    image_files = [
        f"/saved_files/risk/images/{f}" for f in os.listdir(IMG_DIR)
        if f.startswith(session_id) and f.endswith('.png')
    ]

    report = {
        "title": csv_filename.replace(".csv", "").replace("_", " "),
        "csv": f"/saved_files/risk/csvs/{csv_filename}",
        "images": image_files
    }

    risk_reports.append(report)
    return jsonify(risk_reports)

@risk_list_bp.route('/saved_files/risk/csvs/<filename>', methods=['GET'])
def serve_risk_csv(filename):
    return send_from_directory(CSV_DIR, filename)

@risk_list_bp.route('/saved_files/risk/images/<filename>', methods=['GET'])
def serve_risk_image(filename):
    return send_from_directory(IMG_DIR, filename)
