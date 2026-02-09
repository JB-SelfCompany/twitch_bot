<div align="center">

# 📺 Twitch Notification Bot

Telegram bot for tracking Twitch streamers

[![License](https://img.shields.io/github/license/JB-SelfCompany/twitch_bot)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
[![Visitors](https://visitor-badge.laobi.icu/badge?page_id=JB-SelfCompany.twitch_bot)](https://github.com/JB-SelfCompany/twitch_bot)

**[English](#) | [Русский](README.md)**

</div>

---

## ✨ Features

- ➕ Add/remove streamers
- 🔔 Automatic stream notifications
- 📊 Statistics and stream duration
- 💾 SQLite database
- 📱 Single rewritable message

---

## 📋 Requirements

- Python 3.12+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Chat ID from [@userinfobot](https://t.me/userinfobot)

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/JB-SelfCompany/twitch_bot.git
cd twitch_bot

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env

# Run
python bot_main.py
```

### Configuration `.env`

```env
BOT_TOKEN=your_bot_token
CHAT_ID=your_chat_id
CHECK_INTERVAL=120
```

---

## 📚 Usage

1. Open bot in Telegram
2. Send `/start`
3. Click **"Add streamer"**
4. Enter streamer nickname
5. Receive notifications about streams

---

## ⚙️ Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu |
| **Add streamer** | Add to tracking |
| **Streamer list** | View all streamers |
| **Info** | Streamer details |
| **Remove** | Remove from tracking |

---

## 🏗️ Architecture

```
twitch_bot/
├── main.py           # Entry point
├── config.py         # Configuration
├── database/         # SQLite DB
├── handlers/         # Handlers
├── keyboards/        # Keyboards
├── services/         # Twitch API
└── utils/            # Utilities
```

---

## 📄 License

GPLv3 License - see [LICENSE](LICENSE)

---

<div align="center">

Made with ❤️ by <a href="https://github.com/JB-SelfCompany">JB-SelfCompany</a>

</div>
