# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory

# --- 1. การตั้งค่าแอปพลิเคชัน ---
# บอกให้ Flask รู้ว่าไฟล์ Frontend (static files) อยู่ในโฟลเดอร์ชื่อ 'public'
app = Flask(__name__, static_folder='public', static_url_path='')

# ประกาศตัวแปร model ไว้ข้างนอก
model = None

# --- 2. การตั้งค่า Gemini API (ทำครั้งเดียวตอนเซิร์ฟเวอร์เริ่ม) ---
try:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        print("CRITICAL ERROR: 'GOOGLE_API_KEY' is not set in environment variables.")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash-latest')
        print("Gemini API configured and model loaded successfully.")
except Exception as e:
    print(f"An error occurred during Gemini configuration: {e}")

# --- 3. การสร้าง API Endpoints ---

# ===== ส่วนที่เพิ่มเข้ามาใหม่และสำคัญที่สุด =====
@app.route('/')
def serve_index():
    """
    Route นี้จะทำงานเมื่อมีคนเข้าหน้าเว็บหลัก
    มันจะส่งไฟล์ index.html ที่อยู่ในโฟลเดอร์ public กลับไป
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/ask-ai', methods=['POST'])
def ask_ai_route():
    """Endpoint หลักสำหรับรับคำถามและส่งต่อไปยัง Gemini"""
    if not model:
        return jsonify({"error": "AI model is not available."}), 500

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request body."}), 400

    user_prompt = data.get('prompt')
    conversation_history = data.get('history', [])
    
    chat_session_history = []
    for entry in conversation_history:
        role = "model" if entry.get("role") == "assistant" else entry.get("role")
        content = entry.get("content", "")
        if role in ["user", "model"] and content:
            chat_session_history.append({"role": role, "parts": [{"text": content}]})

    try:
        chat_session = model.start_chat(history=chat_session_history)
        response = chat_session.send_message(user_prompt)
        return jsonify({"response": response.text.strip()})
    except Exception as e:
        print(f"Error calling Google Gemini API: {e}")
        return jsonify({"error": f"An error with the Gemini API: {str(e)}"}), 500

# บล็อกนี้จะทำงานเมื่อรันไฟล์โดยตรงเพื่อทดสอบบนเครื่อง
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)