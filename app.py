from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ตั้งค่า Google Gemini API Key จาก environment variable
app = Flask(__name__)
CORS(app)

# ทดสอบโดยใส่ API Key โดยตรง (ชั่วคราวเท่านั้น!)
GOOGLE_API_KEY = "AIzaSyBGJkjXJpXIolN72DGH7Fwc9jtLrXpaK0g"  # <--- แทนที่ด้วย API Key จริงของคุณ

if not GOOGLE_API_KEY:
    print("\nCRITICAL: GOOGLE_API_KEY is not set.")


# --- AI Assistant Endpoint ---
@app.route('/ask-ai', methods=['POST'])
def ask_ai_route():
    if not GOOGLE_API_KEY:
        return jsonify({"error": "Google API Key is not configured."}), 500

    try:
        import os

# Load the API key from an environment variable
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("No GOOGLE_API_KEY set for Flask application")

genai.configure(api_key=GOOGLE_API_KEY)
        print("Google Gemini API Key configured successfully.")
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON."}), 400
        user_prompt = data.get('prompt')
        conversation_history = data.get('history', [])
        if not user_prompt:
            return jsonify({"error": "No prompt provided."}), 400
        chat_session_history = []
        for entry in conversation_history:
            role = entry.get("role")
            content = entry.get("content", "")
            if role == "assistant":
                role = "model"
            if role in ["user", "model"] and content:
                chat_session_history.append({"role": role, "parts": [{"text": content}]})
        chat = model.start_chat(history=chat_session_history)
        response = chat.send_message(user_prompt)
        ai_response_text = response.text.strip()
        return jsonify({"response": ai_response_text})
    except Exception as e:
        print(f"Error calling Google Gemini API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Gemini API Error: {str(e)}"}), 500


if __name__ == '__main__':
    print(f"Starting Flask server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/test-connection', methods=['GET'])
def test_connection_route():
    return "Connection OK from app.py", 200