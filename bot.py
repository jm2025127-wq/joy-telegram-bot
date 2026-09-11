import requests, os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# Render-এর Environment Variable থেকে তথ্য নেওয়া
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8000))
last_song = {}

# Render-এর পোর্ট এরর বা টাইমআউট দূর করার জন্য ডামি ওয়েব সার্ভার
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"Web server started on port {PORT}")
    server.serve_forever()

def get_full_lyrics(song_name):
    try:
        # লিরিক্স ওভিএইচ (Lyrics.ovh) এর অফিশিয়াল গ্লোবাল এবং সঠিক লিংক ফরম্যাট
        url = f"https://lyrics.ovh{song_name}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get('lyrics')
        return None
    except: 
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_song
    if not update.message or not update.message.text:
        return
    chat_id = update.message.chat_id
    text = update.message.text.lower()
    
    if "ফুল" in text or "পুরা" in text:
        if chat_id in last_song:
            song_name = last_song[chat_id]
            await update.message.reply_text("একটু দাঁড়াও, ফুল গান আনতেছি... 🎵")
            lyrics = get_full_lyrics(song_name)
            if lyrics: 
                await update.message.reply_text(f"🎵 {song_name} 🎵\n\n{lyrics}")
            else:
                await update.message.reply_text("দুঃখিত, এই গানের ফুল লিরিক্স খুঁজে পাওয়া যায়নি। 😢")
        else:
            await update.message.reply_text("আগে আমাকে বলো কোন গানটি শুনবে? যেমন: `গান শুনাও তুমি হাসলে`")
            
    elif "গান শুনাও" in text:
        song_name = text.replace("গান শুনাও", "").strip()
        if song_name == "": 
            song_name = "তুমি হাসলে"
        
        last_song[chat_id] = song_name
        await update.message.reply_text(f"একটু দাঁড়াও, '{song_name}' গানটা খুঁজতেছি... 🔍")
        
        lyrics = get_full_lyrics(song_name)
        if lyrics:
            lines = [line for line in lyrics.split("\n") if line.strip()]
            short_lyrics = "\n".join(lines[:2])
            await update.message.reply_text(
                f"🎵 {song_name} 🎵\n\n{short_lyrics}\n\n"
                f"বাকি অংশ বা ফুল গান লাগলে বলো: `ফুল গান` বা `পুরা গান`"
            )
        else:
            await update.message.reply_text(f"দুঃখিত, '{song_name}' গানের লিরিক্স ডাটাবেজে পাওয়া যায়নি। 😢")
    else:
        await update.message.reply_text("আমাকে গান খুঁজতে বলতে লিখুন: `গান শুনাও [গানের নাম]`\nযেমন: `গান শুনাও তুমি হাসলে`")

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN is missing!")
        return

    # ব্যাকগ্রাউন্ডে ডামি ওয়েব সার্ভার চালু করা যাতে Render পোর্ট খুঁজে পায় এবং ফ্রি সার্ভিস সচল থাকে
    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
