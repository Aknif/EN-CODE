# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- 1. การตั้งค่าแอปพลิเคชัน (ทำครั้งเดียว) ---
app = Flask(__name__)
CORS(app)

# ประกาศตัวแปร model ไว้ข้างนอก เพื่อให้ใช้ได้ในทุก request
model = None

# --- 2. การตั้งค่า Gemini API (ทำครั้งเดียวตอนเซิร์ฟเวอร์เริ่มทำงาน) ---
try:
    # อ่าน API Key จาก Environment Variable ของ Render เท่านั้น!
    # นี่คือวิธีที่ปลอดภัยที่สุด
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

    if not GOOGLE_API_KEY:
        # หากไม่ได้ตั้งค่า Key ไว้ ให้แสดงข้อความเตือนใน Log
        print("CRITICAL ERROR: 'GOOGLE_API_KEY' is not set in the environment variables.")
    else:
        # ตั้งค่า API Key และสร้างโมเดล
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash-latest')
        print("Gemini API configured and model loaded successfully.")

except Exception as e:
    # หากเกิดข้อผิดพลาดระหว่างการตั้งค่า ให้พิมพ์ Log ไว้
    print(f"An error occurred during Gemini configuration: {e}")


# --- 3. การสร้าง API Endpoints ---

@app.route('/test-connection', methods=['GET'])
def test_connection_route():
    """Endpoint สำหรับทดสอบว่าเซิร์ฟเวอร์ทำงานอยู่หรือไม่"""
    return "Connection OK from Python server!", 200


@app.route('/ask-ai', methods=['POST'])
def ask_ai_route():
    """Endpoint หลักสำหรับรับคำถามและส่งต่อไปยัง Gemini"""

    # ตรวจสอบก่อนว่าโมเดลถูกสร้างสำเร็จหรือไม่ (จากขั้นตอนที่ 2)
    if not model:
        return jsonify({"error": "AI model is not available. Check server configuration and API Key."}), 500

    # รับข้อมูลจาก Frontend
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be in JSON format."}), 400

    user_prompt = data.get('prompt')
    if not user_prompt:
        return jsonify({"error": "No 'prompt' provided in the request body."}), 400

    # การจัดการประวัติการสนทนา (ถ้ามี)
    conversation_history = data.get('history', [])
    chat_session_history = []
    for entry in conversation_history:
        role = "model" if entry.get("role") == "assistant" else entry.get("role")
        content = entry.get("content", "")
        if role in ["user", "model"] and content:
            chat_session_history.append({"role": role, "parts": [{"text": content}]})

    # เรียกใช้ Gemini API
    try:
        chat_session = model.start_chat(history=chat_session_history)
        response = chat_session.send_message(user_prompt)
        ai_response_text = response.text.strip()
        
        return jsonify({"response": ai_response_text})

    except Exception as e:
        # หากเกิดข้อผิดพลาดระหว่างการเรียก API
        print(f"Error calling Google Gemini API: {e}")
        return jsonify({"error": f"An error occurred with the Gemini API: {str(e)}"}), 500


# --- 4. การรันเซิร์ฟเวอร์ ---
# บล็อกนี้จะทำงานเมื่อรันไฟล์โดยตรง (python app.py) เพื่อทดสอบบนเครื่อง
# บน Render จะใช้ Gunicorn เรียกตัวแปร 'app' โดยตรง
if __name__ == '__main__':
    # ใช้ port 5000 หรือ port อื่นๆ ที่เหมาะสม
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)