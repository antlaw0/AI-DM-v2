from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__)

# Make sure this matches the port your DeepSeek server is actually listening on
LLAMA_SERVER_URL = "http://127.0.0.1:8080/completion"

# Example system prompt for the AI Dungeon Master
SYSTEM_PROMPT = """
You are an AI Dungeon Master for a Dungeons and Dragons 5e campaign. You will need to keep track of everything in order to maintain immersion for the player. This means player HP, amount of gold, equipped gear, spells, etc. You will retrieve relevant database entries for people, places, and things throughout the game and update these files according to outcomes of the player's actions. You are to maintain realism by giving logical outcomes for player actions within the context of the game.
"""

def query_llama(prompt):
    """
    Sends a request to the local DeepSeek llama server and returns parsed JSON output.
    """
    try:
        payload = {
            "prompt": f"<|system|>\n{SYSTEM_PROMPT}\n<|user|>\n{prompt}\n<|assistant|>\n",
            "temperature": 0.7,
            "n_predict": 6000,
            "stop": ["<|user|>", "<|system|>"],
            "stream": False
        }
        response = requests.post(LLAMA_SERVER_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        # DeepSeek returns {"response": "<text>"} or {"content": "<text>"}
        text_output = data.get("response") or data.get("content") or ""
        # Return as JSON object; if AI returns text, wrap in narration field
        return {"narration": text_output.strip()}
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    """
    Serves the main chat interface for the AI Dungeon Master.
    """
    return render_template("index.html")

@app.route("/message", methods=["POST"])
def message():
    """
    Receives messages from the game frontend, queries DeepSeek, and returns JSON.
    """
    user_data = request.json
    user_message = user_data.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    ai_response = query_llama(user_message)
    return jsonify(ai_response)

if __name__ == "__main__":
    # Make sure DeepSeek server is running before starting this Flask server
    app.run(host="0.0.0.0", port=5000, debug=True)
