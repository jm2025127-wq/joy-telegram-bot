import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment থেকে Token নিবে
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# AI Reply এর জন্য ফ্রি API - Groq Llama3
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "হ্যালো! আমি Joy AI Bot 🤖\n"
        "তোমার সাথে গল্প করতে, প্রশ্নের উত্তর দিতে, সাহায্য করতে আমি রেডি।\n"
        "শুধু যা ইচ্ছা লিখে পাঠাও!"
    )

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Groq API call
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192", # ফ্রি + ফাস্ট
        "messages": [
            {"role": "system", "content": "তুমি Joy নামের একটা বন্ধুসুলভ AI। বাংলায় মজা করে, ছোট করে, মানুষের মতো রিপ্লাই দাও।"},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        ai_text = response.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(ai_text)
    except Exception as e:
        await update.message.reply_text("সরি ভাই, এখন একটু সমস্যা হচ্ছে। আবার ট্রাই করো 🙏")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply)) # সব টেক্সট এর রিপ্লাই দিবে

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
