"""Main entry point for Twitch Notification Bot."""
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.models import Database
from database.operations import StreamerOperations, MainMessageOperations
from services.twitch import TwitchService
from handlers import get_routers
from utils.formatters import format_duration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitchBot:
    """Main bot class."""
    
    def __init__(self):
        self.bot = Bot(
            token=config.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self.db = Database(config.db_path)
        self.streamer_ops = StreamerOperations(self.db)
        self.main_msg_ops = MainMessageOperations(self.db)
        self.twitch_service = TwitchService()

        # Register handlers
        for router in get_routers():
            self.dp.include_router(router)

        # Setup dependency injection
        self.dp.workflow_data.update({
            "streamer_ops": self.streamer_ops,
            "main_msg_ops": self.main_msg_ops,
            "twitch_service": self.twitch_service
        })
    
    async def check_streamers_loop(self):
        """Background task to check streamers status."""
        # Initial delay to let bot start
        await asyncio.sleep(10)
        
        while True:
            try:
                await self.check_all_streamers()
                await asyncio.sleep(config.check_interval)
            except Exception as e:
                logger.error(f"Error in check loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def check_all_streamers(self):
        """Check all tracked streamers."""
        streamers = await self.streamer_ops.get_all_streamers()
        
        if not streamers:
            logger.info("No streamers to check")
            return
        
        logger.info(f"Checking {len(streamers)} streamers...")
        
        for streamer_name in streamers:
            try:
                await self.check_streamer(streamer_name)
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Error checking {streamer_name}: {e}", exc_info=True)
    
    async def check_streamer(self, streamer_name: str):
        """Check individual streamer status."""
        is_live = await self.twitch_service.check_stream_status(streamer_name)
        
        if is_live is None:
            logger.warning(f"Could not check status for {streamer_name}")
            return
        
        info = await self.streamer_ops.get_streamer(streamer_name)
        
        if is_live:
            # Streamer is live
            await self.streamer_ops.update_streamer_status(
                streamer_name,
                is_live=True,
                offline_checks=0
            )
            
            # Send notification if not already notified
            if not info['notified_live']:
                await self.send_live_notification(streamer_name)
                await self.streamer_ops.update_streamer_status(
                    streamer_name,
                    is_live=True,
                    notified_live=True,
                    last_stream_start=datetime.now().isoformat()
                )
                logger.info(f"{streamer_name} went live!")
        else:
            # Streamer is offline
            if info['is_live']:
                # Increment offline checks
                offline_checks = info['offline_checks'] + 1
                
                if offline_checks >= 3:
                    # Confirm offline status
                    await self.send_offline_notification(streamer_name, info)
                    await self.streamer_ops.update_streamer_status(
                        streamer_name,
                        is_live=False,
                        notified_live=False,
                        offline_checks=0,
                        last_stream_end=datetime.now().isoformat()
                    )
                    logger.info(f"{streamer_name} went offline")
                else:
                    await self.streamer_ops.update_streamer_status(
                        streamer_name,
                        is_live=True,
                        offline_checks=offline_checks
                    )
                    logger.info(f"{streamer_name} offline check {offline_checks}/3")
    
    async def send_live_notification(self, streamer_name: str):
        """Send notification when streamer goes live."""
        text = (
            f"🔴 <b>Стрим начался!</b>\n\n"
            f"👤 Стример: <b>{streamer_name}</b>\n"
            f"🔗 <a href='https://www.twitch.tv/{streamer_name}'>Смотреть трансляцию</a>"
        )

        try:
            await self.bot.send_message(
                config.chat_id,
                text,
                disable_web_page_preview=True
            )
            logger.info(f"Sent live notification for {streamer_name}")
        except Exception as e:
            logger.error(f"Error sending live notification: {e}", exc_info=True)
    
    async def send_offline_notification(self, streamer_name: str, info: dict):
        """Send notification when streamer goes offline."""
        # Calculate stream duration
        if info['last_stream_start']:
            start_time = datetime.fromisoformat(info['last_stream_start'])
            duration = datetime.now() - start_time
            duration_str = format_duration(duration)
        else:
            duration_str = "Неизвестно"

        text = (
            f"⚫️ <b>Стрим завершен</b>\n\n"
            f"👤 Стример: <b>{streamer_name}</b>\n"
            f"⏱ Длительность: {duration_str}"
        )

        try:
            await self.bot.send_message(
                config.chat_id,
                text
            )
            logger.info(f"Sent offline notification for {streamer_name}")
        except Exception as e:
            logger.error(f"Error sending offline notification: {e}", exc_info=True)
    
    async def start(self):
        """Start the bot."""
        try:
            # Initialize database
            await self.db.connect()
            logger.info("Database initialized")
            
            # Start background tasks
            asyncio.create_task(self.check_streamers_loop())
            logger.info("Started stream checking loop")
            
            logger.info("Bot started successfully")
            await self.dp.start_polling(
                self.bot,
                allowed_updates=self.dp.resolve_used_update_types()
            )
        finally:
            await self.db.close()
            await self.bot.session.close()
            logger.info("Bot stopped")

async def main():
    """Main function."""
    bot = TwitchBot()
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
