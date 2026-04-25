import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Enable CORS to allow requests from the Vue.js frontend
CORS(app)

# Initialize Database
db.init_app(app)

# Register Blueprints (Routes)
from routes.applications import bp as applications_bp
from routes.auth import bp as auth_bp
app.register_blueprint(applications_bp)
app.register_blueprint(auth_bp)

# Import models so SQLAlchemy creates them
from models.application import Application
from models.user import User

# Create database tables automatically
with app.app_context():
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Backend API is live!"}), 200

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
