# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import google.generativeai as genai
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import desc # สำหรับการเรียงลำดับใน Leaderboard

app = Flask(__name__)
app.config['SECRET_KEY'] = 'P!oG-w!A(jslb163'
CORS(app, supports_credentials=True) # เพิ่ม supports_credentials=True สำหรับ session cookies

DB_USERNAME = 'encode_user'
DB_PASSWORD = 'encode_user52025'
DB_HOST = 'localhost'
DB_NAME = 'en-code'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_route'
login_manager.login_message = "กรุณาเข้าสู่ระบบเพื่อเข้าถึงหน้านี้"
login_manager.login_message_category = "info"

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Google Gemini API Key configured successfully.")
    except Exception as e:
        print(f"ERROR configuring Google Gemini API: {e}")
        GOOGLE_API_KEY = None
else:
    print("ERROR: GOOGLE_API_KEY not found in environment variables.")

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0, nullable=False)

    chat_messages = db.relationship('ChatMessage', backref='author_user', lazy='dynamic', foreign_keys='ChatMessage.user_id')
    likes_given = db.relationship('MessageLike', backref='liker_user', lazy='dynamic', foreign_keys='MessageLike.liked_by_user_id')

    def __repr__(self):
        return f'<User {self.username}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(100), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    likes_received = db.relationship('MessageLike', backref='liked_message_info', lazy='dynamic', foreign_keys='MessageLike.message_id', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ChatMessage {self.id} in room {self.room_id}>'

class MessageLike(db.Model):
    __tablename__ = 'message_likes'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='CASCADE'), nullable=False)
    liked_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    __table_args__ = (db.UniqueConstraint('message_id', 'liked_by_user_id', name='uq_message_user_like'),)

    def __repr__(self):
        return f'<MessageLike by user {self.liked_by_user_id} for message {self.message_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Authentication Endpoints (เหมือนเดิม) ---
@app.route('/register', methods=['POST'])
def register_route():
    # ... (โค้ด register เหมือนเดิม) ...
    data = request.get_json(); # ... (ส่วนที่เหลือเหมือนเดิม)
    if not data: return jsonify({"error": "Request body must be JSON"}), 400
    username = data.get('username'); password = data.get('password'); email = data.get('email')
    if not username or not password: return jsonify({"error": "Username and password are required"}), 400
    if User.query.filter_by(username=username).first(): return jsonify({"error": "Username already exists"}), 409
    if email and User.query.filter_by(email=email).first(): return jsonify({"error": "Email already exists"}), 409
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    new_user = User(username=username, password_hash=hashed_password, email=email)
    try:
        db.session.add(new_user); db.session.commit()
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback(); print(f"Error during registration: {e}"); import traceback; traceback.print_exc()
        return jsonify({"error": "Registration failed"}), 500


@app.route('/login', methods=['POST'])
def login_route():
    # ... (โค้ด login เหมือนเดิม) ...
    data = request.get_json(); # ... (ส่วนที่เหลือเหมือนเดิม)
    if not data: return jsonify({"error": "Request body must be JSON"}), 400
    username = data.get('username'); password = data.get('password')
    if not username or not password: return jsonify({"error": "Username and password are required"}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password): return jsonify({"error": "Invalid username or password"}), 401
    login_user(user, remember=data.get('remember_me', False))
    return jsonify({"message": "Login successful", "user": {"id": user.id, "username": user.username, "email": user.email}}), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout_route():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/check_auth_status', methods=['GET'])
def check_auth_status_route():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email, "points": current_user.points}}), 200
    else:
        return jsonify({"logged_in": False}), 200

# --- AI Assistant Endpoint (เหมือนเดิม) ---
@app.route('/ask-ai', methods=['POST'])
@login_required
def ask_ai_route():
    # ... (โค้ด ask-ai เหมือนเดิม, ตรวจสอบ GOOGLE_API_KEY ด้วย) ...
    if not GOOGLE_API_KEY: return jsonify({"error": "Google API Key is not configured."}), 500
    # ... (rest of the function)
    print(f"User '{current_user.username}' (ID: {current_user.id}) is asking the AI.")
    data = request.get_json(); # ... (ส่วนที่เหลือเหมือนเดิม)
    if not data: return jsonify({"error": "Request body must be JSON."}), 400
    user_prompt = data.get('prompt'); conversation_history = data.get('history', [])
    if not user_prompt: return jsonify({"error": "No prompt provided."}), 400
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        chat_session_history = []
        for entry in conversation_history:
            role = entry.get("role"); content = entry.get("content", "")
            if role == "assistant": role = "model"
            if role in ["user", "model"] and content: chat_session_history.append({"role": role, "parts": [{"text": content}]})
        chat = model.start_chat(history=chat_session_history)
        response = chat.send_message(user_prompt)
        ai_response_text = response.text.strip()
        return jsonify({"response": ai_response_text})
    except Exception as e:
        print(f"Error calling Google Gemini API for user {current_user.username}: {e}"); import traceback; traceback.print_exc()
        return jsonify({"error": f"Gemini API Error: {str(e)}"}), 500

# --- Hub (Chat Room) Endpoints ---

@app.route('/hub/messages/<room_id>', methods=['GET'])
@login_required
def get_hub_messages(room_id):
    messages = ChatMessage.query.filter_by(room_id=room_id).order_by(ChatMessage.timestamp.asc()).all()
    output = []
    for msg in messages:
        author_username = User.query.get(msg.user_id).username if User.query.get(msg.user_id) else "Unknown User"
        num_likes = MessageLike.query.filter_by(message_id=msg.id).count()
        # ตรวจสอบว่า current_user ได้ like ข้อความนี้หรือยัง
        user_has_liked = MessageLike.query.filter_by(message_id=msg.id, liked_by_user_id=current_user.id).first() is not None
        output.append({
            "id": msg.id,
            "room_id": msg.room_id,
            "user_id": msg.user_id,
            "username": author_username, # ส่ง username ไปด้วย
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"), # Format timestamp
            "num_likes": num_likes,
            "user_has_liked": user_has_liked
        })
    return jsonify(output), 200

@app.route('/hub/messages', methods=['POST'])
@login_required
def post_hub_message():
    data = request.get_json()
    if not data: return jsonify({"error": "Request body must be JSON"}), 400

    room_id = data.get('room_id')
    content = data.get('content')

    if not room_id or not content:
        return jsonify({"error": "Room ID and content are required"}), 400

    new_message = ChatMessage(room_id=room_id, user_id=current_user.id, content=content)
    try:
        db.session.add(new_message)
        db.session.commit()
        # อาจจะ broadcast message นี้ไปยัง clients อื่นๆ ผ่าน WebSocket ถ้าทำ real-time chat
        return jsonify({
            "message": "Message posted successfully",
            "msg_id": new_message.id,
            "user_id": current_user.id,
            "username": current_user.username,
            "content": new_message.content,
            "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "num_likes": 0,
            "user_has_liked": False
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error posting hub message: {e}")
        return jsonify({"error": "Failed to post message"}), 500

@app.route('/hub/like_message/<int:message_id>', methods=['POST'])
@login_required
def like_hub_message(message_id):
    message_to_like = ChatMessage.query.get_or_404(message_id)
    
    # ป้องกันการ like ข้อความของตัวเอง (optional, ตาม requirement)
    # if message_to_like.user_id == current_user.id:
    #     return jsonify({"error": "You cannot like your own message"}), 403

    # ตรวจสอบว่าเคย like ไปหรือยัง
    existing_like = MessageLike.query.filter_by(message_id=message_id, liked_by_user_id=current_user.id).first()
    if existing_like:
        # ถ้าเคย like แล้ว อาจจะให้ unlike หรือ return error
        db.session.delete(existing_like) # ตัวอย่าง: ทำให้เป็น unlike
        message_author = User.query.get(message_to_like.user_id)
        if message_author and message_author.id != current_user.id : # ลดแต้มเฉพาะเมื่อไม่ใช่การ unlike ข้อความที่ตัวเองเคย like
             message_author.points = max(0, message_author.points - 1) # ป้องกันแต้มติดลบ
        db.session.commit()
        return jsonify({"message": "Message unliked successfully", "liked": False, "num_likes": MessageLike.query.filter_by(message_id=message_id).count()}), 200


    new_like = MessageLike(message_id=message_id, liked_by_user_id=current_user.id)
    message_author = User.query.get(message_to_like.user_id)

    try:
        db.session.add(new_like)
        if message_author and message_author.id != current_user.id: # เพิ่มแต้มให้เจ้าของข้อความ ถ้าไม่ใช่เจ้าของข้อความกดไลค์ตัวเอง
            message_author.points += 1
        db.session.commit()
        return jsonify({"message": "Message liked successfully", "liked": True, "num_likes": MessageLike.query.filter_by(message_id=message_id).count()}), 201
    except Exception as e: # อาจจะเกิดจาก UniqueConstraint ถ้าพยายาม like ซ้ำ (ถึงแม้จะเช็คไปแล้ว)
        db.session.rollback()
        print(f"Error liking message: {e}")
        return jsonify({"error": "Failed to like message"}), 500

@app.route('/hub/leaderboard', methods=['GET'])
@login_required # หรือไม่ก็ได้ถ้าต้องการให้ทุกคนเห็น
def get_leaderboard():
    top_users = User.query.order_by(User.points.desc()).limit(10).all()
    leaderboard = [{"username": user.username, "points": user.points} for user in top_users]
    return jsonify(leaderboard), 200


if __name__ == '__main__':
    if not GOOGLE_API_KEY:
        print("\nCRITICAL: GOOGLE_API_KEY is not set.")

    with app.app_context():
        try:
            db.create_all()
            print("Database tables checked/created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            print(f"DB Config: mysql+pymysql://{DB_USERNAME}:****@{DB_HOST}/{DB_NAME}")


    print(f"Starting Flask server with MySQL on http://127.0.0.1:5000, connected to database '{DB_NAME}'")
    app.run(host='0.0.0.0', port=5000, debug=True)