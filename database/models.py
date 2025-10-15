"""Database models for Twitch Bot."""
import aiosqlite
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Establish database connection."""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info(f"Database connected: {self.db_path}")
    
    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def _create_tables(self):
        """Create necessary tables."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS streamers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                is_live INTEGER DEFAULT 0,
                last_stream_start TEXT,
                last_stream_end TEXT,
                notified_live INTEGER DEFAULT 0,
                offline_checks INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS main_message (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                message_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.commit()
        logger.info("Database tables created/verified")