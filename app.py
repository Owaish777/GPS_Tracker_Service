from flask import Flask, request, jsonify
from time import time
from collections import deque

app = Flask(__name__)

# Store last 100 points per device
# device_id -> deque([points])
location_history = {}

MAX_POINTS = 100

@app.route("/location/update", methods=["POST"])
def update_location():
    data = request.get_json()

    required = ["device_id", "lat", "lon", "accuracy"]
    if not data or not all(k in data for k in required):
        return jsonify({"error": "missing fields"}), 400

    if data["accuracy"] > 25:
        return jsonify({"status": "ignored", "reason": "low accuracy"})

    device_id = data["device_id"]

    point = {
        "lat": data["lat"],
        "lon": data["lon"],
        "accuracy": data["accuracy"],
        "timestamp": data.get("timestamp", int(time()))
    }

    if device_id not in location_history:
        location_history[device_id] = deque(maxlen=MAX_POINTS)

    location_history[device_id].append(point)

    return jsonify({
        "status": "ok",
        "stored_points": len(location_history[device_id])
    })

@app.route("/location/<device_id>", methods=["GET"])
def get_current_location(device_id):
    if device_id not in location_history or not location_history[device_id]:
        return jsonify({"error": "device not found"}), 404

    return jsonify(location_history[device_id][-1])

@app.route("/location/<device_id>/history", methods=["GET"])
def get_location_history(device_id):
    if device_id not in location_history:
        return jsonify({"error": "device not found"}), 404

    return jsonify(list(location_history[device_id]))

if __name__ == "__main__":
    app.run(debug=True)
