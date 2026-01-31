# ⚡ Power Monitor Telegram Bot

Telegram-бот для моніторингу наявності електропостачання
через ping зовнішнього IP.

## 🚀 Функціонал
- визначення стану світла (є / нема)
- алерти при зміні стану
- накопичення статистики
- команда /status

## 🔧 Встановлення

```bash
git clone https://github.com/vtok/monitor_bot.git
cd monitor_bot

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
