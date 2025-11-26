from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
BOT_TOKEN = "<your_token_here>"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("🚀 Bot running…")
app.run_polling()
