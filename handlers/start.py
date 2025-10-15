"""Start command handler."""
from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards.inline import get_main_menu
from database.operations import MainMessageOperations

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, main_msg_ops: MainMessageOperations):
    """Handle /start command."""
    # Delete the command message
    await message.delete()
    
    # Send or update main menu
    msg = await message.answer(
        "🎮 <b>Twitch Notification Bot</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    
    # Save main message ID
    await main_msg_ops.save_main_message(msg.message_id, message.chat.id)
