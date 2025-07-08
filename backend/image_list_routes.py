from flask import Blueprint, jsonify, request, send_from_directory
import os

image_list_bp = Blueprint('image_list', __name__)

IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved_files', 'images'))
CSV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved_files'))  # optional CSV dir

@image_list_bp.route('/api/list_images', methods=['POST'])
def list_images():
    session_id = request.json.get("session_id")
    if not session_id:
        return jsonify({"error": "No session_id provided"}), 400

    plots = []
    for fname in os.listdir(IMAGE_DIR):
        if fname.startswith(session_id) and fname.endswith(".png"):
            base_name = os.path.splitext(fname)[0]  # remove .png
            plots.append({
                "title": base_name,
                "image": f"/saved_files/images/{fname}",
                "csv": f"/saved_files/{base_name}.csv"  # assumes same prefix
            })
    return jsonify(plots)

@image_list_bp.route('/saved_files/images/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@image_list_bp.route('/saved_files/<filename>', methods=['GET'])
def serve_csv(filename):
    return send_from_directory(CSV_DIR, filename)
