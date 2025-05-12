from flask import Blueprint, jsonify, request

location_bp = Blueprint('location', __name__)

@location_bp.route('/location/test', methods=['GET'])
def test_location():
    """Test route for location services"""
    return jsonify({
        "message": "Location service is working",
        "status": "success"
    })