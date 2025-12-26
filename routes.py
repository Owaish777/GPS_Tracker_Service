from flask import Blueprint, request, jsonify
import services

session_bp = Blueprint('session', __name__)

@session_bp.route("/session/start", methods=["POST"])
def start_session():
    data = request.get_json()
    if not data or "device_id" not in data:
        return jsonify({"error": "device_id required"}), 400
    
    result, status_code = services.start_tracking_session(data["device_id"])
    return jsonify(result), status_code

@session_bp.route("/session/<session_id>/location", methods=["POST"])
def push_location(session_id):
    data = request.get_json()
    required = ["lat", "lon", "accuracy"]
    if not data or not all(k in data for k in required):
        return jsonify({"error": "missing fields"}), 400
    
    result, status_code = services.add_gps_point(
        session_id, data["lat"], data["lon"], data["accuracy"]
    )
    return jsonify(result), status_code

@session_bp.route("/session/<session_id>/end", methods=["POST"])
def end_session(session_id):
    result, status_code = services.end_tracking_session(session_id)
    return jsonify(result), status_code

@session_bp.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    result, status_code = services.get_session_summary(session_id)
    return jsonify(result), status_code

@session_bp.route("/session/<session_id>/geojson", methods=["GET"])
def export_session_geojson(session_id):
    result, status_code = services.get_session_geojson(session_id)
    return jsonify(result), status_code