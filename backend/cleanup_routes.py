from flask import Blueprint, request, jsonify
import os

cleanup_bp = Blueprint('cleanup', __name__)
IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved_files', 'images'))

@cleanup_bp.route('/api/cleanup_session', methods=['POST'])
def cleanup_session_images():
    session_id = request.json.get("session_id")
    deleted = []

    print("🔁 Cleanup triggered. Session ID received:", session_id)
    print("📂 Files in images folder:", os.listdir(IMAGE_DIR))

    if not session_id:
        print("❌ No session_id provided.")
        return jsonify({"error": "No session_id provided"}), 400

    for fname in os.listdir(IMAGE_DIR):
        print("🔍 Checking:", fname)
        if fname.startswith(session_id):
            try:
                file_path = os.path.join(IMAGE_DIR, fname)
                os.remove(file_path)
                deleted.append(fname)
                print("✅ Deleted:", fname)
            except Exception as e:
                print("❌ Failed to delete:", fname, "Error:", str(e))

    print("🧹 Deletion complete:", deleted)
    return jsonify({"deleted": deleted}), 200
