from flask import Flask, request, jsonify
from time import time

app = Flask(__name__)

# In-memory store
current_locations = {}

@app.route("/location/update", methods=["POST"])
def update_location():
    data = request.get_json()

    required = ["device_id", "lat", "lon", "accuracy"]
    if not all(k in data for k in required):
        return jsonify({"error": "missing fields"}), 400

    device_id = data["device_id"]

    current_locations[device_id] = {
        "lat": data["lat"],
        "lon": data["lon"],
        "accuracy": data["accuracy"],
        "timestamp": data.get("timestamp", int(time()))
    }

    return jsonify({"status": "ok"})

@app.route("/location/<device_id>", methods=["GET"])
def get_location(device_id):
    if device_id not in current_locations:
        return jsonify({"error": "device not found"}), 404

    return jsonify(current_locations[device_id])

if __name__ == "__main__":
    app.run(debug=True)
