# Twitch Notification Bot

Telegram бот для отслеживания стримеров на Twitch с автоматическими уведомлениями о начале и окончании трансляций.

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.15-blue)](https://docs.aiogram.dev/)

## Возможности

- ➕ Добавление/удаление стримеров
- 🔔 Автоматические уведомления о стримах
- 📊 Статистика и длительность трансляций
- 💾 SQLite база данных
- 📱 Единое перезаписываемое сообщение

## Требования

- Python 3.13+
- Telegram Bot Token от [@BotFather](https://t.me/BotFather)
- Chat ID от [@userinfobot](https://t.me/userinfobot)

## Установка

### 1. Установка pyenv и Python 3.13

Установка pyenv
```bash
curl https://pyenv.run | bash
```

Добавление в .bashrc
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
```

Установка Python 3.13
```bash
pyenv install 3.13.5
pyenv virtualenv 3.13.5 twitch_bot
```

### 2. Настройка проекта

Клонирование
```bash
git clone https://github.com/your_username/twitch_bot.git
cd twitch_bot
```

Активация окружения
```bash
pyenv local twitch_bot
```

Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Конфигурация

Создание .env
```bash
cp .env.example .env
nano .env
```

Укажите в `.env`:
```bash
BOT_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
CHECK_INTERVAL=120
```

### 4. Запуск

```bash
python bot_main.py
```

## Использование

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Нажмите **"➕ Добавить стримера"**
4. Введите никнейм стримера
5. Получайте уведомления о стримах

## Команды

- `/start` - Главное меню
- **Добавить стримера** - Добавить в отслеживание
- **Список стримеров** - Просмотр всех стримеров
- **Информация** - Детали о стримере
- **Удалить** - Удалить из отслеживания

## Структура проекта

```
twitch_bot/
├── main.py # Точка входа
├── config.py # Конфигурация
├── requirements.txt # Зависимости
├── database/ # SQLite БД
├── handlers/ # Обработчики
├── keyboards/ # Клавиатуры
├── services/ # Twitch API
└── utils/ # Утилиты
```

## Решение проблем

**Бот не запускается?**

Проверьте логи
```bash
sudo journalctl -u twitch_bot -f
```

**База заблокирована?**

```bash
sudo systemctl restart twitch_bot
```

## Автор

**JB-SelfCompany**
- GitHub: [@JB-SelfCompany](https://github.com/JB-SelfCompany)
