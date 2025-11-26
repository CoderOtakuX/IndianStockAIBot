# 🇮🇳 Indian Stock AI Bot 🤖💹

**An intelligent Telegram bot that delivers real-time Indian stock analysis, AI insights, and sentiment evaluation — all in one place.**

---

## 🧠 Features

✅ **Stock Analysis:**  
Fetches live data (current price, day range, 52-week range, etc.) from NSE-listed companies using Yahoo Finance.

✅ **AI Expert Summary:**  
Generates detailed investment analysis (EMA, RSI, MACD, support/resistance, sentiment, and buy/hold/sell verdicts).

✅ **Live News Integration:**  
Automatically fetches the latest news headlines for each stock from Google News RSS and includes them in the report.

✅ **AI Chat Mode:**  
Chat directly with an integrated AI assistant for general market queries — powered by LLaMA/DeepSeek models.

✅ **(Coming soon)** — FinBERT-based sentiment scoring for each news headline 📰  
✅ **(Coming soon)** — Auto alerts when price crosses thresholds 🔔  
✅ **(Coming soon)** — Portfolio tracker with profit/loss updates 💰  
✅ **(Coming soon)** — AI comparison between multiple stocks ⚔️  

---

## 🧩 Project Structure
📁 INDIAN STOCK AGENT PYTHON/
├── main.py # Main Telegram bot logic
├── config.py # API keys (excluded via .gitignore)
├── requirements.txt # Dependencies list
├── README.md # Documentation
├── .gitignore # Ignore rules
└── stockbot_env/ # Virtual environment (ignored)


---

## 🧠 Features

- **Real-time stock analysis:**  
  Fetches NSE stock data like price, range, and yearly high/low using Yahoo Finance.
  
- **AI expert summary:**  
  Generates deep technical & sentiment analysis — RSI, EMA, MACD, support/resistance, short/long-term outlook, and investment verdict.

- **News integration:**  
  Retrieves and analyzes up-to-date market news headlines for context.

- **Chat mode:**  
  A natural language chat interface for market questions, insights, and general discussions.

- **Future updates:**
  - FinBERT sentiment scoring for news articles 📰  
  - Automatic stock alerts when thresholds are met 🔔  
  - Portfolio tracking with daily gain/loss summaries 💰  
  - AI-based stock comparison between competitors ⚔️  

---

## 💻 Tech Stack

- **Python 3.10+**
- **python-telegram-bot v21**
- **yfinance**
- **feedparser**
- **requests**
- **Hugging Face Inference API**
- **OpenRouter (DeepSeek / LLaMA) models**

---

## ⚙️ Installation

### 1️⃣ Clone this repository
```bash
git clone https://github.com/<yourusername>/IndianStockAIBot.git
cd IndianStockAIBot
python -m venv stockbot_env
stockbot_env\Scripts\activate   # On Windows
pip install -r requirements.txt
