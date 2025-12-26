from collections import deque

MAX_POINTS = 100

# session_id -> session data
sessions = {}

# device_id -> active session_id
active_sessions = {}