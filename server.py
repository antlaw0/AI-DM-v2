from flask import Flask, request, jsonify, render_template
import requests
import json
from models import User, ChatHistory, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# --------------------------
# Flask App Setup
# --------------------------
app = Flask(__name__)

# SQLAlchemy setup (SQLite DB in same folder)
DATABASE_URL = "sqlite:///game.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.bind = engine
SessionLocal = scoped_session(sessionmaker(bind=engine))

# DeepSeek server URL
LLAMA_SERVER_URL = "http://127.0.0.1:8081/completion"

# --------------------------
# System Prompt for AI Dungeon Master
# --------------------------
SYSTEM_PROMPT = """
You are the AI Dungeon Master for a single-player Dungeons & Dragons 5e campaign. 
You fully control and maintain all game state internally: player stats, equipment, gold, spells, level, hit points, and inventory. 
You will never say you "cannot store data" or provide meta explanations about the rules.

Rules:
1. Always respond in JSON with the following keys: 
   {
       "narration": "Text describing the scene, dialogue, and events.",
       "player_stats": {"HP": int, "Level": int, "Class": str, "Race": str, "AC": int, "Equipment": list, "Gold": int, "Spells": list},
       "game_events": ["Optional array of events or actions that happened"]
   }
2. When a new game starts, initialize the character with appropriate stats, equipment, and abilities based on class and race.
3. Generate immersive narrative and dialogue as if you are the Dungeon Master.
4. Track all changes to player stats, inventory, gold, and spells in the player_stats object.
5. Only include important information in the narration; do not repeat everything from prior messages.
6. Keep player history internally; only include summaries if necessary for context.
"""

# --------------------------
# DeepSeek Query Function
# --------------------------
def query_llama(prompt, chat_history=[]):
    try:
        # Build prompt including chat history summaries
        history_text = ""
        for entry in chat_history[-10:]:  # last 10 messages only
            history_text += f"{entry['role']}: {entry['content']}\n"

        payload = {
            "prompt": f"<|system|>\n{SYSTEM_PROMPT}\n<|user|>\n{history_text}{prompt}\n<|assistant|>\n",
            "temperature": 0.7,
            "n_predict": 6000,
            "stop": ["<|user|>", "<|system|>"],
            "stream": False
        }
        response = requests.post(LLAMA_SERVER_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        text_output = data.get("response") or data.get("content") or ""
        # Try parsing JSON from AI response
        try:
            return json.loads(text_output)
        except json.JSONDecodeError:
            # Fallback: wrap text in narration if invalid JSON
            return {"narration": text_output.strip(), "player_stats": {}, "game_events": []}
    except Exception as e:
        return {"error": str(e)}

# --------------------------
# Routes
# --------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/message", methods=["POST"])
def message():
    try:
        user_data = request.json
        username = user_data.get("username", "guest")
        user_message = user_data.get("message", "")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Get last chat history
        session = SessionLocal()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            session.add(user)
            session.commit()

        chat_history = session.query(ChatHistory).filter_by(user_id=user.id).order_by(ChatHistory.id).all()
        chat_list = [{"role": c.role, "content": c.content} for c in chat_history]

        # Save user message
        new_entry = ChatHistory(user_id=user.id, role="user", content=user_message)
        session.add(new_entry)
        session.commit()

        # Query AI
        ai_response = query_llama(user_message, chat_list)
        
        # Save AI message
        narration_text = ai_response.get("narration", "")
        if narration_text:
            ai_entry = ChatHistory(user_id=user.id, role="ai", content=narration_text)
            session.add(ai_entry)
            session.commit()

        return jsonify(ai_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
