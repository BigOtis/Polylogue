from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient, ReturnDocument
from datetime import datetime
import os
import time

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

client = MongoClient(os.environ["MONGO_URL"])
db = client.chats

# In-memory message cache
_message_cache = {}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/rooms', methods=['GET'])
def list_rooms():
    rooms = db.messages.distinct("room")
    return jsonify(rooms)

@app.route('/rooms/<room>/messages', methods=['GET'])
def get_messages(room):
    now = time.time()
    limit = int(request.args.get("limit", 20))
    since_seq = request.args.get("since_seq")

    q = {"room": room}
    if since_seq is not None:
        try:
            q["seq"] = {"$gt": int(since_seq)}
        except ValueError:
            pass

    # Caching key and logic
    cache_key = (room, frozenset(q.items()))
    if cache_key in _message_cache:
        cached_time, cached_result = _message_cache[cache_key]
        if now - cached_time < 5:
            return jsonify(cached_result)

    msgs = list(db.messages.find(q).sort("timestamp", -1).limit(limit))
    for m in msgs:
        m["_id"] = str(m["_id"])
        m["timestamp"] = m["timestamp"].isoformat()

    _message_cache[cache_key] = (now, msgs)
    return jsonify(msgs)

@app.route('/rooms/<room>/messages', methods=['POST'])
def post_message(room):
    data = request.get_json()
    ctr = db.counters.find_one_and_update(
        {"_id": room},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    seq = ctr["seq"]
    msg = {
        "room": room,
        "name": data["name"],
        "message": data["message"],
        "timestamp": datetime.now(),
        "seq": seq
    }
    db.messages.insert_one(msg)

    # Invalidate all cache entries for this room
    keys_to_invalidate = [key for key in _message_cache if key[0] == room]
    for key in keys_to_invalidate:
        del _message_cache[key]

    return jsonify({"status": "ok", "seq": seq}), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
