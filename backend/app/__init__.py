from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from app.routes.saved_plots import saved_bp
    app.register_blueprint(saved_bp)

    return app
