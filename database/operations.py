"""Database operations for Twitch Bot."""
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from database.models import Database

logger = logging.getLogger(__name__)

class StreamerOperations:
    """Operations for streamer management."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def add_streamer(self, name: str) -> bool:
        """Add a new streamer to tracking."""
        try:
            name = name.lower()
            await self.db.connection.execute(
                "INSERT INTO streamers (name) VALUES (?)",
                (name,)
            )
            await self.db.connection.commit()
            logger.info(f"Streamer {name} added to tracking")
            return True
        except Exception as e:
            logger.error(f"Error adding streamer {name}: {e}")
            return False
    
    async def remove_streamer(self, name: str) -> bool:
        """Remove a streamer from tracking."""
        try:
            name = name.lower()
            cursor = await self.db.connection.execute(
                "DELETE FROM streamers WHERE name = ?",
                (name,)
            )
            await self.db.connection.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Streamer {name} removed from tracking")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing streamer {name}: {e}")
            return False
    
    async def get_all_streamers(self) -> List[str]:
        """Get list of all tracked streamers."""
        cursor = await self.db.connection.execute(
            "SELECT name FROM streamers ORDER BY name"
        )
        rows = await cursor.fetchall()
        return [row["name"] for row in rows]
    
    async def get_streamer(self, name: str) -> Optional[Dict[str, Any]]:
        """Get streamer information."""
        cursor = await self.db.connection.execute(
            "SELECT * FROM streamers WHERE name = ?",
            (name.lower(),)
        )
        row = await cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def update_streamer_status(
        self,
        name: str,
        is_live: bool,
        notified_live: bool = None,
        offline_checks: int = None,
        last_stream_start: str = None,
        last_stream_end: str = None
    ):
        """Update streamer status."""
        updates = ["is_live = ?"]
        params = [1 if is_live else 0]
        
        if notified_live is not None:
            updates.append("notified_live = ?")
            params.append(1 if notified_live else 0)
        
        if offline_checks is not None:
            updates.append("offline_checks = ?")
            params.append(offline_checks)
        
        if last_stream_start is not None:
            updates.append("last_stream_start = ?")
            params.append(last_stream_start)
        
        if last_stream_end is not None:
            updates.append("last_stream_end = ?")
            params.append(last_stream_end)
        
        params.append(name.lower())
        
        query = f"UPDATE streamers SET {', '.join(updates)} WHERE name = ?"
        await self.db.connection.execute(query, params)
        await self.db.connection.commit()
        logger.info(f"Updated status for {name}")

class MainMessageOperations:
    """Operations for main message management."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def save_main_message(self, message_id: int, chat_id: int):
        """Save or update main message ID."""
        await self.db.connection.execute("""
            INSERT INTO main_message (id, message_id, chat_id, updated_at)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                message_id = excluded.message_id,
                chat_id = excluded.chat_id,
                updated_at = excluded.updated_at
        """, (message_id, chat_id, datetime.now().isoformat()))
        await self.db.connection.commit()
        logger.info(f"Main message saved: {message_id}")
    
    async def get_main_message(self) -> Optional[Dict[str, Any]]:
        """Get main message information."""
        cursor = await self.db.connection.execute(
            "SELECT message_id, chat_id FROM main_message WHERE id = 1"
        )
        row = await cursor.fetchone()
        
        if row:
            return dict(row)
        return None
