from flask import Blueprint, jsonify, send_from_directory
import os

inventory_bp = Blueprint('inventory', __name__)
INVENTORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved_files', 'inventory'))

@inventory_bp.route('/api/list_inventory', methods=['GET'])
def list_inventory_reports():
    reports = []
    for fname in os.listdir(INVENTORY_DIR):
        if fname.endswith(".csv"):
            reports.append({
                "title": fname.replace("_", " "),
                "csv": f"/saved_files/inventory/{fname}"
            })
    return jsonify(reports)

@inventory_bp.route('/saved_files/inventory/<filename>', methods=['GET'])
def get_inventory_file(filename):
    return send_from_directory(INVENTORY_DIR, filename)
