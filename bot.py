import os
import telebot
import google.generativeai as genai
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("AI টেলিগ্রাম বট তৈরি হচ্ছে...")

@bot.message_handler(func=lambda message: True)
def reply_with_ai(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "দুঃখিত, আমি এই মুহূর্তে উত্তর দিতে পারছি না।")

if __name__ == "__main__":
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
