from flask import Flask
from flask_cors import CORS  # ✅ Add this
from auth_routes import auth_bp
from cleanup_routes import cleanup_bp
app = Flask(__name__)
from image_list_routes import image_list_bp
from inventory_routes import inventory_bp
from route_list_routes import route_list_bp
from risk_list_risks import risk_list_bp

CORS(app)  # ✅ Enable CORS globally
app.register_blueprint(risk_list_bp)

app.register_blueprint(inventory_bp)
app.register_blueprint(route_list_bp)  
app.register_blueprint(cleanup_bp)
app.register_blueprint(image_list_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)
