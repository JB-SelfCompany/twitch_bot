"""Twitch service for checking stream status."""
import aiohttp
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TwitchService:
    """Service for interacting with Twitch."""
    
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    async def check_stream_status(self, streamer_name: str) -> Optional[bool]:
        """Check if streamer is live."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f'https://www.twitch.tv/{streamer_name}'
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        match = re.search(r'"isLiveBroadcast":\s*true', html)
                        return match is not None
                    else:
                        logger.error(f"Error fetching {streamer_name}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error checking {streamer_name}: {e}")
            return None
