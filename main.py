import logging
import yfinance as yf
import requests
import feedparser
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Safety check
if not all([BOT_TOKEN, OPENROUTER_API_KEY, HUGGINGFACE_TOKEN]):
    raise EnvironmentError("❌ Missing one or more required environment variables.")


logging.basicConfig(level=logging.INFO)

# ──────────────────────── STOCK DATA ────────────────────────
def fetch_stock_data(symbol):
    if not symbol.endswith(".NS"):
        symbol += ".NS"
    stock = yf.Ticker(symbol)
    info = stock.info
    if "regularMarketPrice" not in info or info["regularMarketPrice"] is None:
        raise RuntimeError("⚠️ Yahoo data unavailable")

    return {
        "symbol": symbol,
        "name": info.get("longName", symbol),
        "exchange": info.get("exchange", "NSE"),
        "industry": info.get("industry", "N/A"),
        "currency": info.get("currency", "INR"),
        "current": info.get("regularMarketPrice"),
        "previous": info.get("regularMarketPreviousClose"),
        "high": info.get("regularMarketDayHigh"),
        "low": info.get("regularMarketDayLow"),
        "year_high": info.get("fiftyTwoWeekHigh"),
        "year_low": info.get("fiftyTwoWeekLow"),
    }

# ──────────────────────── NEWS FETCH ────────────────────────
def fetch_news(company):
    q = urllib.parse.quote(f"{company} stock India")
    url = f"https://news.google.com/rss/search?q={q}"
    feed = feedparser.parse(url)
    return [{"headline": e.title, "url": e.link} for e in feed.entries[:5]]

# ──────────────────────── AI SUMMARY ────────────────────────
def ai_analysis(data, news):
    news_text = "\n".join([f"- {n['headline']} ({n['url']})" for n in news]) or "No recent news found."

    prompt = f"""
Provide a professional, detailed stock analysis for {data['name']} ({data['symbol']}).

Exchange: {data['exchange']}
Industry: {data['industry']}
Price: {data['currency']} {data['current']}
Range: {data['low']} - {data['high']}
52W Range: {data['year_low']} - {data['year_high']}

Recent News:
{news_text}

Include in your report:
1️⃣ Technical indicators (RSI, EMA, MACD)
2️⃣ Market sentiment based on news
3️⃣ Support and resistance levels
4️⃣ Short-term vs long-term outlook
5️⃣ Final investment verdict (Buy/Hold/Sell)
"""

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": prompt}],
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=90)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ DeepSeek failed: {e}")

    # Fallback: HuggingFace Router
    try:
        res = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers={"Authorization": f"Bearer {HUGGINGFACE_TOKEN}", "Content-Type": "application/json"},
            json={
                "model": "meta-llama/Llama-3.1-8B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=90,
        )
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ HuggingFace failed: {e}")

    return "⚠️ AI summary currently unavailable."

# ──────────────────────── AI CHAT ────────────────────────
def ai_chat(query):
    try:
        res = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers={"Authorization": f"Bearer {HUGGINGFACE_TOKEN}", "Content-Type": "application/json"},
            json={
                "model": "meta-llama/Llama-3.1-8B-Instruct",
                "messages": [{"role": "user", "content": query}],
            },
            timeout=60,
        )
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"].strip()
        return f"⚠️ Chat API error: {res.status_code}"
    except Exception as e:
        return f"⚠️ Chat failed: {e}"

# ──────────────────────── TELEGRAM HANDLERS ────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 AI Stock Summary", callback_data="summary")],
        [InlineKeyboardButton("💬 Chat Mode", callback_data="chat")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Welcome to Indian Stock AI Bot 🇮🇳*\n\nChoose one of the options below:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "summary":
        await query.message.reply_text("📈 Send any Indian stock name (e.g. Reliance, TCS, Infosys)")
    elif query.data == "chat":
        await query.message.reply_text("💬 Chat mode activated! Just type your question — no need for `chat:` prefix.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # 🧠 Smart detection: if it's conversational
    if len(text.split()) > 2 and not text.isupper():
        await update.message.reply_text("💬 Thinking...")
        answer = ai_chat(text)
        await update.message.reply_text(answer, parse_mode="Markdown")
        return

    try:
        # Otherwise, treat as stock query
        data = fetch_stock_data(text.upper())
        news = fetch_news(data["name"])
        await update.message.reply_text("🧠 Analyzing stock data...")
        ai_text = ai_analysis(data, news)

        # Build formatted message
        message = (
            f"*📊 {data['name']} ({data['symbol']})*\n"
            f"Exchange: {data['exchange']}\n"
            f"Industry: {data['industry']}\n\n"
            f"💰 *Current Price:* {data['currency']} {data['current']}\n"
            f"Previous Close: {data['previous']}\n"
            f"Day Range: {data['low']} - {data['high']}\n"
            f"52W Range: {data['year_low']} - {data['year_high']}\n\n"
            f"📰 *Top News:*\n"
            + "\n".join([f"• [{n['headline']}]({n['url']})" for n in news])
            + "\n\n💬 *AI Expert Summary:*\n"
            + ai_text
        )

        await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ──────────────────────── MAIN ────────────────────────
def main():
    print("🚀 Bot is running... (CTRL + C to stop)")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
