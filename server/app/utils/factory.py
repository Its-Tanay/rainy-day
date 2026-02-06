from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.api.itinerary import itinerary_v1
from app.api.auth import auth_v1
from app.api.health import health_v1
from app.utils.config import load_config

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    config = load_config()
    app.config.update(config)

    app.config['JWT_SECRET_KEY'] = config['JWT_SECRET_KEY']
    jwt = JWTManager(app)

    app.register_blueprint(health_v1)
    app.register_blueprint(itinerary_v1)
    app.register_blueprint(auth_v1)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Request Not Found'}), 404

    return app