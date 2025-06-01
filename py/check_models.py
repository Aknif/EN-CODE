import google.generativeai as genai
import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Available models:")
    for m in genai.list_models():
        # ตรวจสอบว่า model รองรับ 'generateContent' (สำหรับ text-only input)
        # หรือ 'embedContent' หรือ method อื่นๆ ที่เกี่ยวข้องกับ chat
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (Supports: {m.supported_generation_methods})")
        # หรือถ้าใช้ chat session object อาจจะต้องดูว่ารองรับการ start_chat
        # if any(method_name for method_name in m.supported_generation_methods if 'chat' in method_name.lower()):
        #     print(f"- {m.name} (Potentially supports chat)")

else:
    print("GOOGLE_API_KEY not set.")