# Twitch Notification Telegram Bot

Телеграм-бот на Python для получения уведомлений о начале трансляций с ресурса [twitch.tv](https://twitch.tv). Подразумевается, что у вас уже установлен Python 3.11.x (на 3.12.x возникают ошибки). Используется библиотека `aiogram` версии 2.25.2.

## Оглавление

- [Возможности](#возможности)
- [Установка](#установка)
- [Запуск](#запуск)
- [Заметки](#заметки)
- [Поддержка](#поддержка)

## Возможности

- Добавление стримеров для отслеживания трансляций
- Отслеживание начала последней трансляции, конца трансляции, общее время трансляции

## Установка

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/JB-SelfCompany/twitch_bot
    cd twitch_bot
    ```

    #### Опционально (рекомендуется устанавливать библиотеки в виртуальное окружение)
   
    Установка Python 3.11 для Linux:

       sudo apt-get install software-properties-common && sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update && sudo apt install python3.11 python3.11-dev python3.11-venv

    Установка Python 3.11 для Windows производится с официального [сайта](https://www.python.org/downloads/release/python-31110/). 

    Создайте и активируйте виртуальное окружение для Python:

    ```bash
    python3.11 -m venv myenv
    source myenv/bin/activate          # Для Linux
    python -m myenv\Scripts\activate   # Для Windows
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Создайте бота в Telegram:

    - Откройте Telegram и найдите бота [BotFather](https://t.me/BotFather).
    - Начните диалог, отправив команду `/start`.
    - Введите команду `/newbot`, чтобы создать нового бота.
    - Следуйте инструкциям BotFather, чтобы:
        - Придумать имя для вашего бота (например, `UserBot`).
        - Придумать уникальное имя пользователя для бота (например, `User_bot`). Оно должно оканчиваться на `_bot`.
    - После создания бота BotFather отправит вам токен для доступа к API. Его запросит бот во время первоначальной инициализации.

## Запуск

1. Запустите бота:

    ```bash
    python3.11 bot_twitch.py
    ```
    
2. Добавьте бота в Telegram и отправьте команду `/start` для начала работы.

## Заметки

Вы можете запускать бота как службу на вашем сервере. Для этого:

1. Скопируйте файл `twitch_bot.service` в директорию `/etc/systemd/system/`:

    ```bash
    sudo cp twitch_bot.service /etc/systemd/system/
    ```

2. Отредактируйте параметры внутри файла с помощью `nano` (или любого удобного текстового редактора):

    ```bash
    sudo nano /etc/systemd/system/twitch_bot.service
    ```
    
3. Перезагрузите системный демон и запустите службу:

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start twitch_bot.service
    sudo systemctl enable twitch_bot.service
    ```

## Поддержка

Если у вас возникли вопросы или проблемы с установкой и использованием бота, создайте [issue](https://github.com/JB-SelfCompany/twitch_bot/issues) в этом репозитории или обратитесь к администратору.

- [Telegram](https://t.me/Mystery_TF)
- [Matrix](https://matrix.to/#/@jack_benq:shd.company)
