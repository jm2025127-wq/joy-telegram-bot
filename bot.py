import requests, os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
last_song = {}

def get_full_lyrics(song_name):
    try:
        url = f"https://api.lyrics.ovh/v1/Bangla/{song_name}"
        res = requests.get(url, timeout=5)
        return res.json().get('lyrics')
    except: return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_song
    chat_id = update.message.chat_id
    text = update.message.text.lower()
    
    if "ফুল" in text or "পুরা" in text:
        if chat_id in last_song:
            song_name = last_song[chat_id]
            await update.message.reply_text("একটু দাঁড়াও, ফুল গান আনতেছি... 🎵")
            lyrics = get_full_lyrics(song_name)
            if lyrics: await update.message.reply_text(f"🎵 {song_name} 🎵\n\n{lyrics}")
    
    elif "গান শুনাও" in text:
        song_name = text.replace("গান শুনাও", "").strip()
        if song_name == "": song_name = "তুমি হাসলে"
        last_song[chat_id] = song_name
        lyrics = get_full_lyrics(song_name)
        if lyrics:
            short_lyrics = "\n".join(lyrics.split("\n")[:2])
            await update.message.reply_text(f"🎵 {song_name} 🎵\n\n{short_lyrics}\n\nফুল গান লাগলে বলো `গান শুনাও ফুল`")
    else:
        await update.message.reply_text("আমাকে বলো `গান শুনাও [গানের নাম]`")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
