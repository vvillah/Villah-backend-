from flask import Flask, request, jsonify
import uuid
from datetime import datetime

app = Flask(_name_)

# In-memory database
database = {
    "users": {},
    "posts": {},
    "messages": {},
    "groups": {},
    "stories": {},
    "notifications": {},
    "marketplace": {},
    "events": {},
    "settings": {},
    "live_streams": {},
    "ai_profiles": {},
    "pro_features": {},
    "coins": {},
    "ads": {},
    "games": {},
    "academy": {},
    "shadow_ai": {},
    "holo_rooms": {},
    "quests": {},
    "language_translations": {},
    "owner_dashboard": {
        "admins": [],
        "logs": [],
        "statistics": {}
    }
}

# Helpers
def generate_id():
    return str(uuid.uuid4())

def timestamp():
    return datetime.now().isoformat()

# Owner Dashboard Functions
def create_admin(username):
    admin_id = generate_id()
    database["owner_dashboard"]["admins"].append({
        "id": admin_id,
        "username": username,
        "created_at": timestamp()
    })
    return {"status": "success", "admin_id": admin_id}

def log_event(action, details):
    database["owner_dashboard"]["logs"].append({
        "id": generate_id(),
        "action": action,
        "details": details,
        "timestamp": timestamp()
    })

def update_statistics():
    database["owner_dashboard"]["statistics"] = {
        "total_users": len(database["users"]),
        "total_posts": len(database["posts"]),
        "total_messages": len(database["messages"]),
        "total_groups": len(database["groups"]),
        "total_streams": len(database["live_streams"]),
        "total_market_items": len(database["marketplace"]),
        "total_notifications": sum(len(n) for n in database["notifications"].values())
    }

# Core User Functions
def register_user(username, email, password):
    uid = generate_id()
    database['users'][uid] = {
        "username": username,
        "email": email,
        "password": password,
        "created_at": timestamp(),
        "balance": 0,
        "pro_status": False,
        "language": "en",
        "theme": "default"
    }
    log_event("register", f"User {username} registered.")
    update_statistics()
    return {"status": "success", "user_id": uid}

def login_user(email, password):
    for uid, user in database['users'].items():
        if user['email'] == email and user['password'] == password:
            return {"status": "success", "user_id": uid}
    return {"status": "fail", "reason": "Invalid credentials"}

def create_post(user_id, content, media_url=None):
    pid = generate_id()
    database['posts'][pid] = {
        "user_id": user_id,
        "content": content,
        "media_url": media_url,
        "created_at": timestamp(),
        "likes": [],
        "comments": []
    }
    log_event("post_created", f"Post by {user_id}")
    update_statistics()
    return {"status": "success", "post_id": pid}

def send_message(sender_id, receiver_id, message, media=None):
    mid = generate_id()
    database['messages'][mid] = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message,
        "media": media,
        "timestamp": timestamp(),
        "status": "sent"
    }
    log_event("message_sent", f"From {sender_id} to {receiver_id}")
    update_statistics()
    return {"status": "success", "message_id": mid}

def earn_coins(user_id, action):
    earn_rate = {"post": 10, "comment": 5, "like": 2, "watch": 3, "stream": 20}
    coins = earn_rate.get(action, 0)
    if user_id in database["users"]:
        database["users"][user_id]["balance"] += coins
    return {"status": "earned", "coins": coins}

def recharge_account(user_id, amount):
    if user_id in database["users"]:
        database["users"][user_id]["balance"] += amount
        return {"status": "recharged", "balance": database["users"][user_id]["balance"]}
    return {"status": "fail"}

def activate_pro(user_id, method="coin"):
    if user_id in database["users"]:
        user = database["users"][user_id]
        if method == "coin" and user["balance"] >= 100:
            user["balance"] -= 100
            user["pro_status"] = True
            return {"status": "upgraded"}
        return {"status": "fail", "reason": "Insufficient coins"}
    return {"status": "fail", "reason": "User not found"}

def get_ai_response(user_id, prompt, mode="honest"):
    modes = {
        "honest": f"[Honest AI] {prompt}",
        "romantic": f"[Romantic AI] You are loved. {prompt}",
        "naughty": f"[Naughty AI] Let's keep it spicy. {prompt}",
        "funny": f"[Funny AI] Haha! {prompt}",
        "sexual": f"[Sexual AI] I’m blushing... {prompt}"
    }
    return {"response": modes.get(mode, f"[AI] {prompt}")}

def add_notification(user_id, content):
    nid = generate_id()
    if user_id not in database["notifications"]:
        database["notifications"][user_id] = []
    database["notifications"][user_id].append({
        "id": nid,
        "content": content,
        "read": False,
        "timestamp": timestamp()
    })
    return {"status": "notified"}

def get_user_data(user_id):
    return database["users"].get(user_id, {"status": "not found"})

# --- Flask API Routes ---
@app.route('/register', methods=['POST'])
def api_register():
    data = request.json
    return jsonify(register_user(data["username"], data["email"], data["password"]))

@app.route('/login', methods=['POST'])
def api_login():
    data = request.json
    return jsonify(login_user(data["email"], data["password"]))

@app.route('/post', methods=['POST'])
def api_post():
    data = request.json
    return jsonify(create_post(data["user_id"], data["content"], data.get("media_url")))

@app.route('/message', methods=['POST'])
def api_message():
    data = request.json
    return jsonify(send_message(data["sender_id"], data["receiver_id"], data["message"], data.get("media")))

@app.route('/earn', methods=['POST'])
def api_earn():
    data = request.json
    return jsonify(earn_coins(data["user_id"], data["action"]))

@app.route('/recharge', methods=['POST'])
def api_recharge():
    data = request.json
    return jsonify(recharge_account(data["user_id"], data["amount"]))

@app.route('/activate_pro', methods=['POST'])
def api_pro():
    data = request.json
    return jsonify(activate_pro(data["user_id"], data.get("method", "coin")))

@app.route('/ai', methods=['POST'])
def api_ai():
    data = request.json
    return jsonify(get_ai_response(data["user_id"], data["prompt"], data.get("mode", "honest")))

@app.route('/notify', methods=['POST'])
def api_notify():
    data = request.json
    return jsonify(add_notification(data["user_id"], data["content"]))

@app.route('/user/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_data(user_id))

@app.route('/admin/create', methods=['POST'])
def api_create_admin():
    data = request.json
    return jsonify(create_admin(data["username"]))

@app.route('/admin/logs', methods=['GET'])
def api_logs():
    return jsonify(database["owner_dashboard"]["logs"])

@app.route('/admin/stats', methods=['GET'])
def api_stats():
    update_statistics()
    return jsonify(database["owner_dashboard"]["statistics"])

# Run the Flask app
if _name_ == '_main_':
    app.run(debug=True)
