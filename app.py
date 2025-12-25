from flask import Flask, request, jsonify
from time import time
from collections import deque
import uuid

app = Flask(__name__)

MAX_POINTS = 100

# session_id -> session data
sessions = {}

# device_id -> active session_id
active_sessions = {}

# -----------------------------
# Start a tracking session
# -----------------------------
@app.route("/session/start", methods=["POST"])
def start_session():
    data = request.get_json()
    if not data or "device_id" not in data:
        return jsonify({"error": "device_id required"}), 400

    device_id = data["device_id"]

    # Prevent multiple active sessions
    if device_id in active_sessions:
        return jsonify({
            "error": "session already active",
            "session_id": active_sessions[device_id]
        }), 400

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "device_id": device_id,
        "start_time": int(time()),
        "end_time": None,
        "status": "ACTIVE",
        "gps_points": deque(maxlen=MAX_POINTS)
    }

    active_sessions[device_id] = session_id

    return jsonify({
        "session_id": session_id,
        "status": "started"
    })


# -----------------------------
# Push GPS point to a session
# -----------------------------
@app.route("/session/<session_id>/location", methods=["POST"])
def push_location(session_id):
    if session_id not in sessions:
        return jsonify({"error": "invalid session"}), 404

    session = sessions[session_id]

    if session["status"] != "ACTIVE":
        return jsonify({"error": "session not active"}), 400

    data = request.get_json()
    required = ["lat", "lon", "accuracy"]
    if not data or not all(k in data for k in required):
        return jsonify({"error": "missing fields"}), 400

    if data["accuracy"] > 25:
        return jsonify({"status": "ignored", "reason": "low accuracy"})

    point = {
        "lat": data["lat"],
        "lon": data["lon"],
        "accuracy": data["accuracy"],
        "timestamp": int(time())
    }

    session["gps_points"].append(point)

    return jsonify({
        "status": "ok",
        "points_in_session": len(session["gps_points"])
    })


# -----------------------------
# End a tracking session
# -----------------------------
@app.route("/session/<session_id>/end", methods=["POST"])
def end_session(session_id):
    if session_id not in sessions:
        return jsonify({"error": "invalid session"}), 404

    session = sessions[session_id]

    if session["status"] != "ACTIVE":
        return jsonify({"error": "session already ended"}), 400

    session["status"] = "ENDED"
    session["end_time"] = int(time())

    device_id = session["device_id"]
    active_sessions.pop(device_id, None)

    return jsonify({
        "status": "ended",
        "duration_sec": session["end_time"] - session["start_time"],
        "points_collected": len(session["gps_points"])
    })


# -----------------------------
# Get session summary
# -----------------------------
@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    if session_id not in sessions:
        return jsonify({"error": "invalid session"}), 404

    session = sessions[session_id]

    return jsonify({
        "device_id": session["device_id"],
        "start_time": session["start_time"],
        "end_time": session["end_time"],
        "status": session["status"],
        "points_collected": len(session["gps_points"])
    })


if __name__ == "__main__":
    app.run(debug=True)
