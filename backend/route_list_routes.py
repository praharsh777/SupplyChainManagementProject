from flask import Blueprint, jsonify, send_from_directory
import os

route_list_bp = Blueprint('route_list', __name__)
ROUTE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved_files', 'routes'))

@route_list_bp.route('/api/list_routes', methods=['GET'])
def list_routes():
    reports = []
    for fname in os.listdir(ROUTE_DIR):
        if fname.endswith('.csv'):
            base = fname.replace('.csv', '')
            html_name = f"{base}_map.html"
            reports.append({
                "title": base.replace("_", " "),
                "csv": f"/saved_files/routes/{fname}",
                "map": f"/saved_files/routes/{html_name}" if os.path.exists(os.path.join(ROUTE_DIR, html_name)) else None
            })
    return jsonify(reports)

@route_list_bp.route('/saved_files/routes/<filename>', methods=['GET'])
def serve_route_files(filename):
    return send_from_directory(ROUTE_DIR, filename)
