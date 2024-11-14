import asyncio
import configparser
import logging
import json
import aiohttp
import re
from datetime import datetime
import locale
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    locale_available = False
else:
    locale_available = True

def format_datetime_russian(dt):
    if locale_available:
        return dt.strftime('%d %B %Y, %H:%M')
    else:
        months = ['', 'января', 'февраля', 'марта', 'апреля', 'мая',
                  'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
        day = dt.day
        month = months[dt.month]
        year = dt.year
        hour = dt.hour
        minute = dt.minute
        return f'{day} {month} {year}, {hour:02d}:{minute:02d}'

config = configparser.ConfigParser()
settings_file = 'settings.ini'

if not config.read(settings_file):
    print("Файл settings.ini не найден. Пожалуйста, введите необходимые данные.")
    BOT_TOKEN = input("Введите токен телеграмм бота: ").strip()
    CHAT_ID = input("Введите ваш телеграмм ID: ").strip()

    config['DEFAULT'] = {
        'BOT_TOKEN': BOT_TOKEN,
        'CHAT_ID': CHAT_ID
    }

    with open(settings_file, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print("Настройки сохранены в settings.ini")
else:
    try:
        BOT_TOKEN = config['DEFAULT']['BOT_TOKEN']
        CHAT_ID = config['DEFAULT']['CHAT_ID']
    except KeyError as e:
        logger.error(f"Ошибка в настройках: отсутствует ключ {e}")
        exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

DB_FILE = 'db.txt'

def load_data():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    # Добавляем 'notified_live' для каждого стримера, если отсутствует
    for streamer in data.values():
        if 'notified_live' not in streamer:
            streamer['notified_live'] = False
    return data

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

class Form(StatesGroup):
    waiting_for_streamer_name = State()

def add_streamer(streamer_name):
    streamer_name = streamer_name.lower()
    if streamer_name not in data:
        data[streamer_name] = {
            'is_live': False,
            'last_stream_start': None,
            'last_stream_end': None,
            'notified_live': False  # Новый флаг
        }
        save_data(data)
        logger.info(f"Streamer {streamer_name} added to tracking.")
        return True
    else:
        logger.info(f"Streamer {streamer_name} is already being tracked.")
        return False

def remove_streamer(streamer_name):
    streamer_name = streamer_name.lower()
    if streamer_name in data:
        del data[streamer_name]
        save_data(data)
        logger.info(f"Streamer {streamer_name} removed from tracking.")
        return True
    else:
        logger.error(f"Streamer {streamer_name} not found in data.")
        return False

def get_streamers():
    return list(data.keys())

async def check_streamer(streamer_name):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        async with aiohttp.ClientSession() as session:
            url = f'https://www.twitch.tv/{streamer_name}'
            async with session.get(url, headers=headers) as response:
                html = await response.text()
                if re.search(r'"isLiveBroadcast":\s*true', html):
                    logger.info(f"Стример {streamer_name} в эфире")
                    if not data[streamer_name]['is_live']:
                        data[streamer_name]['is_live'] = True
                        data[streamer_name]['last_stream_start'] = datetime.now().isoformat()
                        data[streamer_name]['notified_live'] = True
                        save_data(data)
                        await bot.send_message(CHAT_ID, f'Стример {streamer_name} сейчас в эфире!\nhttps://www.twitch.tv/{streamer_name}')
                else:
                    logger.info(f"Стример {streamer_name} не в эфире")
                    if data[streamer_name]['is_live']:
                        last_stream_start = datetime.fromisoformat(data[streamer_name]['last_stream_start'])
                        stream_duration = datetime.now() - last_stream_start
                        data[streamer_name]['is_live'] = False
                        data[streamer_name]['last_stream_end'] = datetime.now().isoformat()
                        data[streamer_name]['notified_live'] = False
                        save_data(data)
                        duration_str = str(stream_duration).split('.')[0]
                        await bot.send_message(CHAT_ID, f'Стример {streamer_name} закончил трансляцию. Длительность стрима: {duration_str}')
    except Exception as e:
        logger.error(f'Ошибка при проверке стримера {streamer_name}: {e}')

async def check_streamers():
    while True:
        streamers = get_streamers()
        async with aiohttp.ClientSession() as session:
            for streamer in streamers:
                try:
                    await check_streamer_in_session(streamer, session)
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f'Ошибка при проверке стримера {streamer}: {e}')
        await asyncio.sleep(60)

async def check_streamer_in_session(streamer_name, session):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    url = f'https://www.twitch.tv/{streamer_name}'
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        if re.search(r'"isLiveBroadcast":\s*true', html):
            logger.info(f"Стример {streamer_name} в эфире")
            if not data[streamer_name]['is_live']:
                # Стример только что начал стрим
                data[streamer_name]['is_live'] = True
                data[streamer_name]['last_stream_start'] = datetime.now().isoformat()
                data[streamer_name]['notified_live'] = True
                save_data(data)
                await bot.send_message(CHAT_ID, f'Стример {streamer_name} сейчас в эфире!\nhttps://www.twitch.tv/{streamer_name}')
            elif not data[streamer_name]['notified_live']:
                # Бот перезапустился, а стример все еще в эфире, но уведомление не отправлено
                data[streamer_name]['notified_live'] = True
                save_data(data)
                await bot.send_message(CHAT_ID, f'Стример {streamer_name} сейчас в эфире!\nhttps://www.twitch.tv/{streamer_name}')
        else:
            logger.info(f"Стример {streamer_name} не в эфире")
            if data[streamer_name]['is_live']:
                last_stream_start = datetime.fromisoformat(data[streamer_name]['last_stream_start'])
                stream_duration = datetime.now() - last_stream_start
                data[streamer_name]['is_live'] = False
                data[streamer_name]['last_stream_end'] = datetime.now().isoformat()
                data[streamer_name]['notified_live'] = False
                save_data(data)
                duration_str = str(stream_duration).split('.')[0]
                await bot.send_message(CHAT_ID, f'Стример {streamer_name} закончил трансляцию. Длительность стрима: {duration_str}')

menu_cb = CallbackData('menu', 'action')
streamer_cb = CallbackData('streamer', 'name', 'action')

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать!", reply_markup=types.ReplyKeyboardRemove())
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Добавить стримера", callback_data=menu_cb.new(action='add_streamer')),
        InlineKeyboardButton("Список стримеров", callback_data=menu_cb.new(action='list_streamers'))
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.callback_query_handler(menu_cb.filter(action='add_streamer'))
async def add_streamer_handler(callback_query: types.CallbackQuery, state: FSMContext):
    msg = await callback_query.message.edit_text("Пожалуйста, введите ник стримера, которого хотите добавить:")
    await Form.waiting_for_streamer_name.set()
    await state.update_data(last_bot_message_id=msg.message_id)
    await callback_query.answer()

@dp.message_handler(state=Form.waiting_for_streamer_name)
async def process_streamer_name(message: types.Message, state: FSMContext):
    streamer_name = message.text.strip().lower()
    data_state = await state.get_data()
    last_bot_message_id = data_state.get('last_bot_message_id')
    if add_streamer(streamer_name):
        try:
            await bot.edit_message_text(
                f"Стример {streamer_name} добавлен для отслеживания.",
                chat_id=message.chat.id,
                message_id=last_bot_message_id
            )
        except Exception as e:
            logger.error(f"Ошибка при редактировании сообщения: {e}")
            await message.answer(f"Стример {streamer_name} добавлен для отслеживания.")
        logger.info(f"Пользователь {message.from_user.id} добавил стримера {streamer_name}")
        await check_streamer(streamer_name)
    else:
        try:
            await bot.edit_message_text(
                f"Стример {streamer_name} уже отслеживается.",
                chat_id=message.chat.id,
                message_id=last_bot_message_id
            )
        except Exception as e:
            logger.error(f"Ошибка при редактировании сообщения: {e}")
            await message.answer(f"Стример {streamer_name} уже отслеживается.")
    await state.finish()
    # Возвращаем главное меню, редактируя текущее сообщение
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Добавить стримера", callback_data=menu_cb.new(action='add_streamer')),
        InlineKeyboardButton("Список стримеров", callback_data=menu_cb.new(action='list_streamers'))
    )
    await bot.edit_message_text("Выберите действие:", chat_id=message.chat.id, message_id=last_bot_message_id, reply_markup=keyboard)

@dp.callback_query_handler(menu_cb.filter(action='list_streamers'))
async def list_streamers_handler(callback_query: types.CallbackQuery):
    streamers = get_streamers()
    keyboard = InlineKeyboardMarkup()
    if not streamers:
        keyboard.add(
            InlineKeyboardButton("Назад", callback_data=menu_cb.new(action='back_to_main'))
        )
        await callback_query.message.edit_text("Список стримеров пуст.", reply_markup=keyboard)
        await callback_query.answer()
        return

    for streamer in streamers:
        # Добавляем значок, если стример в эфире
        streamer_info = data.get(streamer, {})
        is_live = streamer_info.get('is_live', False)
        if is_live:
            button_text = f"✅ {streamer}"
        else:
            button_text = streamer
        keyboard.add(
            InlineKeyboardButton(button_text, callback_data=streamer_cb.new(name=streamer, action='show_info'))
        )
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data=menu_cb.new(action='back_to_main'))
    )
    await callback_query.message.edit_text("Выберите стримера для получения информации:", reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(menu_cb.filter(action='back_to_main'))
async def back_to_main(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Добавить стримера", callback_data=menu_cb.new(action='add_streamer')),
        InlineKeyboardButton("Список стримеров", callback_data=menu_cb.new(action='list_streamers'))
    )
    await callback_query.message.edit_text("Выберите действие:", reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(streamer_cb.filter(action='show_info'))
async def show_streamer_info(callback_query: types.CallbackQuery, callback_data: dict):
    streamer_name = callback_data['name']
    if streamer_name in data:
        streamer_info = data[streamer_name]
        is_live = streamer_info['is_live']
        last_start = streamer_info['last_stream_start']
        last_end = streamer_info['last_stream_end']
        status_emoji = '🟢' if is_live else '🔴'
        status_text = f"{status_emoji} В эфире" if is_live else f"{status_emoji} Не в эфире"
        if last_start:
            last_start_dt = datetime.fromisoformat(last_start)
            last_stream_date = format_datetime_russian(last_start_dt)
        else:
            last_stream_date = "Нет данных"
        if last_start and last_end:
            start_time = datetime.fromisoformat(last_start)
            end_time = datetime.fromisoformat(last_end)
            duration = end_time - start_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f'{int(hours)} часов {int(minutes)} минут'
        else:
            duration_str = 'Нет данных'
        info_message = (
            f"Статус: {status_text}\n"
            f"Последняя трансляция: {last_stream_date}\n"
            f"Длительность последней трансляции: {duration_str}\n"
            f"https://www.twitch.tv/{streamer_name}"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Удалить", callback_data=streamer_cb.new(name=streamer_name, action='delete'))
        )
        keyboard.add(
            InlineKeyboardButton("Назад", callback_data=menu_cb.new(action='list_streamers'))
        )
        await callback_query.message.edit_text(info_message, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text("Стример не найден.")
        logger.error(f"Стример {streamer_name} не найден в данных.")
        await cmd_start(callback_query.message)
    await callback_query.answer()

@dp.callback_query_handler(streamer_cb.filter(action='delete'))
async def confirm_delete_streamer(callback_query: types.CallbackQuery, callback_data: dict):
    streamer_name = callback_data['name']
    logger.info(f"Пользователь {callback_query.from_user.id} пытается удалить стримера {streamer_name}")
    if remove_streamer(streamer_name):
        # Перезаписываем текущее сообщение, сообщая об удалении и показывая главное меню
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Добавить стримера", callback_data=menu_cb.new(action='add_streamer')),
            InlineKeyboardButton("Список стримеров", callback_data=menu_cb.new(action='list_streamers'))
        )
        await callback_query.message.edit_text(f"Стример {streamer_name} удален из отслеживания.\n\nВыберите действие:", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text("Ошибка при удалении стримера.")
        logger.error(f"Ошибка при удалении стримера {streamer_name}")
    await callback_query.answer()

@dp.message_handler()
async def unknown_message(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} отправил неизвестное сообщение: {message.text}")
    await message.reply("Пожалуйста, используйте кнопки для управления ботом.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_streamers())
    executor.start_polling(dp, skip_updates=True)
