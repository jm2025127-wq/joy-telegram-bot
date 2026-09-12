import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PORT = int(os.environ.get("PORT", 8000))

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"AI Bot is alive and kicking!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"Web server started on port {PORT}")
    server.serve_forever()

def ask_gemini_ai(user_message):
    if not GEMINI_API_KEY:
        return "ভুল: সার্ভারে Gemini API Key সেট করা নেই! অনুগ্রহ করে Render-এর Environment ভ্যারিয়েবলে GEMINI_API_KEY যোগ করুন।"
        
    # সঠিক Gemini API Endpoint এবং Model Name (gemini-1.5-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"তুমি একটি বন্ধুত্বপূর্ণ ও অত্যন্ত বুদ্ধিমান বাংলা এআই টেলিগ্রাম বট। "
                    f"তুমি ব্যবহারকারীদের খুব বিনম্র ও সুন্দরভাবে বাংলায় উত্তর দেবে। "
                    f"ইউজার তোমাকে গান, লিরিক্স, গল্প, সাধারণ জ্ঞান, রেসিপি যা-ই জিজ্ঞেস করুক, "
                    f"তুমি আসল ChatGPT বা Gemini এআই-এর মতো গুছিয়ে চমৎকার উত্তর দেবে। "
                    f"ইউজারের মেসেজটি হলো: {user_message}"
                )
            }]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            # Response parsing ঠিক করা হয়েছে
            res_data = response.json()
            ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
            return ai_text
        else:
            print(f"API Error Code: {response.status_code}, Response: {response.text}")
            return "দুঃখিত, এআই সার্ভার থেকে এই মুহূর্তে কোনো সাড়া পাওয়া যাচ্ছে না। একটু পরে আবার চেষ্টা করুন। 😢"
    except Exception as e:
        print(f"Exception: {e}")
        return "দুঃখিত, নেটওয়ার্কের সমস্যার কারণে এআই উত্তর দিতে পারছে না। 😢"

async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text
    chat_id = update.message.chat_id
    
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    ai_reply = ask_gemini_ai(user_text)
    await update.message.reply_text(ai_reply)

def main():
    if not TELEGRAM_TOKEN:
        print("Error: BOT_TOKEN environment variable is missing!")
        return

    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))
    
    print("AI Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
