"""Configuration management for Twitch Bot."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    """Bot configuration."""
    
    bot_token: str
    chat_id: int
    check_interval: int = 120
    db_path: str = "twitch_bot.db"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        bot_token = os.getenv("BOT_TOKEN")
        chat_id = os.getenv("CHAT_ID")
        
        if not bot_token:
            raise ValueError("BOT_TOKEN is not set in environment")
        if not chat_id:
            raise ValueError("CHAT_ID is not set in environment")
            
        return cls(
            bot_token=bot_token,
            chat_id=int(chat_id),
            check_interval=int(os.getenv("CHECK_INTERVAL", "120")),
            db_path=os.getenv("DB_PATH", "twitch_bot.db")
        )

# Global config instance
config = Config.from_env()