"""Inline keyboards for Twitch Bot."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

def get_main_menu() -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить стримера", callback_data="add_streamer")
    builder.button(text="📋 Список стримеров", callback_data="list_streamers")
    builder.adjust(1)
    return builder.as_markup()

def get_back_button() -> InlineKeyboardMarkup:
    """Get back to menu button."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    return builder.as_markup()

def get_streamers_list(streamers: List[tuple]) -> InlineKeyboardMarkup:
    """Get streamers list keyboard."""
    builder = InlineKeyboardBuilder()
    
    for name, is_live in streamers:
        emoji = "🟢" if is_live else "🔴"
        builder.button(
            text=f"{emoji} {name}",
            callback_data=f"streamer:{name}"
        )
    
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_streamer_info_keyboard(streamer_name: str) -> InlineKeyboardMarkup:
    """Get streamer info keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Удалить", callback_data=f"delete:{streamer_name}")
    builder.button(text="🔙 Назад", callback_data="list_streamers")
    builder.adjust(1)
    return builder.as_markup()
