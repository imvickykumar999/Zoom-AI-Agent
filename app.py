from flask import Flask, render_template, jsonify
import requests
import json
import os
import time
import base64
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Initialize Flask and Limiter ---
app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])  # Global limit

# --- Configuration ---
TOKEN_FILE = 'zoom_token.json'
client_id = os.getenv("ZOOM_CLIENT_ID") or "your_client_id"
client_secret = os.getenv("ZOOM_CLIENT_SECRET") or "your_client_secret"

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("error.html", error="🚫 Too many requests. Please wait and try again in a minute."), 429

# --- Token Utilities ---
def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token = json.load(f)
        if 'expires_at' not in token:
            token['expires_at'] = time.time() + token.get('expires_in', 3600)
            save_token(token)
        return token
    raise Exception("Token file not found. Run initial OAuth flow.")

def save_token(token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token, f, indent=2)
    print("💾 Token updated and saved.")

def is_token_expired(token):
    return time.time() > (token.get('expires_at', 0) - 120)

def refresh_access_token(token):
    print("🔄 Refreshing access token...")
    url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "grant_type": "refresh_token",
        "refresh_token": token['refresh_token']
    }
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        new_token = response.json()
        new_token['expires_at'] = time.time() + new_token['expires_in']
        return new_token
    raise Exception(f"Failed to refresh token: {response.status_code} {response.text}")

# --- Zoom API ---
def create_zoom_meeting(access_token):
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": "Zoom Meeting via Flask",
        "type": 2,
        "start_time": "2025-07-07T10:00:00",
        "duration": 30,
        "timezone": "Asia/Kolkata",
        "settings": {
            "join_before_host": True
        }
    }
    response = requests.post(url, headers=headers, json=payload)

    # Handle Zoom rate limiting gracefully
    if response.status_code == 429:
        return {
            "error": "Zoom rate limit reached. Please try again later.",
            "status_code": 429
        }

    if response.status_code == 201:
        return response.json()

    raise Exception(f"Failed to create meeting: {response.status_code} {response.text}")

# --- Flask Route ---
@app.route('/', methods=['GET'])
@limiter.limit("5 per minute")  # Limit per IP
def create_meeting_endpoint():
    try:
        token = load_token()
        if is_token_expired(token):
            token = refresh_access_token(token)
            save_token(token)

        meeting = create_zoom_meeting(token['access_token'])

        # If rate-limited by Zoom, return graceful message
        if isinstance(meeting, dict) and meeting.get("status_code") == 429:
            return jsonify(meeting), 429

        return render_template("meeting_success.html", meeting=meeting)

    except Exception as e:
        return render_template("error.html", error=str(e)), 500

# --- Run Server ---
if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=3000,
    )
