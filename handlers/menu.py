"""Menu handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InaccessibleMessage
from keyboards.inline import get_main_menu

router = Router()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Return to main menu."""
    # Check if message is accessible
    if isinstance(callback.message, InaccessibleMessage):
        await callback.answer("❌ Сообщение недоступно. Используйте /start", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🎮 <b>Twitch Notification Bot</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()