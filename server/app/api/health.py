"""
Health check endpoint for monitoring service availability.
"""
from flask import Blueprint, jsonify

health_v1 = Blueprint('health_v1', __name__, url_prefix='/health')

@health_v1.route('', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'trip-planner-api'
    }), 200
