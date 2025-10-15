"""Streamer management handlers."""
from aiogram import Router, F, types
from aiogram.types import InaccessibleMessage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from database.operations import StreamerOperations, MainMessageOperations
from keyboards.inline import (
    get_back_button,
    get_streamers_list,
    get_streamer_info_keyboard,
    get_main_menu
)
from utils.formatters import format_datetime_russian, format_duration
from services.twitch import TwitchService

router = Router()

class AddStreamerStates(StatesGroup):
    """States for adding streamer."""
    waiting_for_name = State()

@router.callback_query(F.data == "add_streamer")
async def add_streamer_start(callback: types.CallbackQuery, state: FSMContext):
    """Start adding streamer process."""
    # Check if message is accessible
    if isinstance(callback.message, InaccessibleMessage):
        await callback.answer("❌ Сообщение недоступно. Используйте /start", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📝 Введите ник стримера на Twitch:",
        reply_markup=get_back_button()
    )
    await state.set_state(AddStreamerStates.waiting_for_name)
    await callback.answer()

@router.message(AddStreamerStates.waiting_for_name)
async def process_streamer_name(
    message: types.Message,
    state: FSMContext,
    streamer_ops: StreamerOperations,
    main_msg_ops: MainMessageOperations,
    twitch_service: TwitchService
):
    """Process streamer name input."""
    streamer_name = message.text.strip().lower()
    
    # Delete user's message
    await message.delete()
    
    # Get main message info
    main_msg = await main_msg_ops.get_main_message()
    
    # Add streamer to database
    success = await streamer_ops.add_streamer(streamer_name)
    
    if success:
        # Check initial status
        is_live = await twitch_service.check_stream_status(streamer_name)
        
        if is_live:
            await streamer_ops.update_streamer_status(
                streamer_name,
                is_live=True,
                last_stream_start=datetime.now().isoformat(),
                notified_live=False
            )
        
        text = f"✅ Стример <b>{streamer_name}</b> добавлен для отслеживания!"
    else:
        text = f"⚠️ Стример <b>{streamer_name}</b> уже отслеживается."
    
    # Update main message
    if main_msg:
        try:
            await message.bot.edit_message_text(
                text=text + "\n\nВыберите действие:",
                chat_id=main_msg['chat_id'],
                message_id=main_msg['message_id'],
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
        except Exception as e:
            # If edit fails, send new message
            new_msg = await message.answer(
                text + "\n\nВыберите действие:",
                reply_markup=get_main_menu()
            )
            await main_msg_ops.save_main_message(new_msg.message_id, message.chat.id)
    else:
        # Send new main message
        new_msg = await message.answer(
            text + "\n\nВыберите действие:",
            reply_markup=get_main_menu()
        )
        await main_msg_ops.save_main_message(new_msg.message_id, message.chat.id)
    
    await state.clear()

@router.callback_query(F.data == "list_streamers")
async def list_streamers(callback: types.CallbackQuery, streamer_ops: StreamerOperations):
    """Show list of tracked streamers."""
    # Check if message is accessible
    if isinstance(callback.message, InaccessibleMessage):
        await callback.answer("❌ Сообщение недоступно. Используйте /start", show_alert=True)
        return
    
    streamers = await streamer_ops.get_all_streamers()
    
    if not streamers:
        await callback.message.edit_text(
            "📋 Список стримеров пуст.\n\n"
            "Добавьте стримера для начала отслеживания.",
            reply_markup=get_back_button()
        )
        await callback.answer()
        return
    
    # Get status for each streamer
    streamers_with_status = []
    for name in streamers:
        info = await streamer_ops.get_streamer(name)
        streamers_with_status.append((name, info['is_live']))
    
    await callback.message.edit_text(
        "📋 <b>Список отслеживаемых стримеров:</b>\n\n"
        "Выберите стримера для просмотра информации:",
        reply_markup=get_streamers_list(streamers_with_status),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("streamer:"))
async def show_streamer_info(callback: types.CallbackQuery, streamer_ops: StreamerOperations):
    """Show detailed streamer information."""
    # Check if message is accessible
    if isinstance(callback.message, InaccessibleMessage):
        await callback.answer("❌ Сообщение недоступно. Используйте /start", show_alert=True)
        return
    
    streamer_name = callback.data.split(":")[1]
    info = await streamer_ops.get_streamer(streamer_name)
    
    if not info:
        await callback.answer("❌ Стример не найден", show_alert=True)
        return
    
    # Format status
    status_emoji = "🟢" if info['is_live'] else "🔴"
    status_text = "В эфире" if info['is_live'] else "Не в эфире"
    
    # Format last stream date
    if info['last_stream_start']:
        last_start_dt = datetime.fromisoformat(info['last_stream_start'])
        last_stream_date = format_datetime_russian(last_start_dt)
    else:
        last_stream_date = "Нет данных"
    
    # Format duration
    if info['last_stream_start'] and info['last_stream_end']:
        start_time = datetime.fromisoformat(info['last_stream_start'])
        end_time = datetime.fromisoformat(info['last_stream_end'])
        duration = end_time - start_time
        duration_str = format_duration(duration)
    else:
        duration_str = "Нет данных"
    
    text = (
        f"👤 <b>{streamer_name}</b>\n\n"
        f"{status_emoji} Статус: <b>{status_text}</b>\n"
        f"📅 Последняя трансляция: {last_stream_date}\n"
        f"⏱ Длительность: {duration_str}\n\n"
        f"🔗 <a href='https://www.twitch.tv/{streamer_name}'>Открыть канал</a>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_streamer_info_keyboard(streamer_name),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delete:"))
async def delete_streamer(callback: types.CallbackQuery, streamer_ops: StreamerOperations):
    """Delete streamer from tracking."""
    # Check if message is accessible
    if isinstance(callback.message, InaccessibleMessage):
        await callback.answer("❌ Сообщение недоступно. Используйте /start", show_alert=True)
        return
    
    streamer_name = callback.data.split(":")[1]
    success = await streamer_ops.remove_streamer(streamer_name)
    
    if success:
        text = f"✅ Стример <b>{streamer_name}</b> удален из отслеживания."
    else:
        text = f"❌ Ошибка при удалении стримера <b>{streamer_name}</b>."
    
    await callback.message.edit_text(
        text + "\n\nВыберите действие:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()