import uuid
from time import time
from collections import deque
from storage import sessions, active_sessions, MAX_POINTS

def start_tracking_session(device_id):
    if device_id in active_sessions:
        return {"error": "session already active", "session_id": active_sessions[device_id]}, 400

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "device_id": device_id,
        "start_time": int(time()),
        "end_time": None,
        "status": "ACTIVE",
        "gps_points": deque(maxlen=MAX_POINTS)
    }
    active_sessions[device_id] = session_id
    return {"session_id": session_id, "status": "started"}, 201

def add_gps_point(session_id, lat, lon, accuracy):
    if session_id not in sessions:
        return {"error": "invalid session"}, 404

    session = sessions[session_id]
    if session["status"] != "ACTIVE":
        return {"error": "session not active"}, 400

    if accuracy > 25:
        return {"status": "ignored", "reason": "low accuracy"}, 200

    point = {
        "lat": lat,
        "lon": lon,
        "accuracy": accuracy,
        "timestamp": int(time())
    }
    session["gps_points"].append(point)
    return {"status": "ok", "points_in_session": len(session["gps_points"])}, 200

def end_tracking_session(session_id):
    if session_id not in sessions:
        return {"error": "invalid session"}, 404

    session = sessions[session_id]
    if session["status"] != "ACTIVE":
        return {"error": "session already ended"}, 400

    session["status"] = "ENDED"
    session["end_time"] = int(time())
    active_sessions.pop(session["device_id"], None)

    return {
        "status": "ended",
        "duration_sec": session["end_time"] - session["start_time"],
        "points_collected": len(session["gps_points"])
    }, 200

def get_session_summary(session_id):
    if session_id not in sessions:
        return {"error": "invalid session"}, 404
    
    session = sessions[session_id]
    return {
        "device_id": session["device_id"],
        "start_time": session["start_time"],
        "end_time": session["end_time"],
        "status": session["status"],
        "points_collected": len(session["gps_points"])
    }, 200

def get_session_geojson(session_id):
    if session_id not in sessions:
        return {"error": "invalid session"}, 404

    session = sessions[session_id]
    points = list(session["gps_points"])
    if not points:
        return {"error": "no gps data"}, 400

    coordinates = [[p["lon"], p["lat"]] for p in points]
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {k: session[k] for k in ["device_id", "start_time", "end_time"]},
            "geometry": {"type": "LineString", "coordinates": coordinates}
        }]
    }, 200

def get_all_sessions():
    """Returns a summary list of all sessions."""
    summary_list = []
    for sid, data in sessions.items():
        summary_list.append({
            "session_id": sid,
            "device_id": data["device_id"],
            "status": data["status"],
            "points_collected": len(data["gps_points"]),
            "start_time": data["start_time"]
        })
    return summary_list, 200

def delete_session(session_id):
    """Removes a session from storage and clears active status if necessary."""
    if session_id not in sessions:
        return {"error": "invalid session"}, 404
    
    session = sessions.pop(session_id)
    if active_sessions.get(session["device_id"]) == session_id:
        active_sessions.pop(session["device_id"], None)
        
    return {"status": "deleted", "session_id": session_id}, 200