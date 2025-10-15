"""Formatting utilities."""
from datetime import datetime, timedelta
import locale
import logging

logger = logging.getLogger(__name__)

# Try to set Russian locale
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    LOCALE_AVAILABLE = True
except locale.Error:
    LOCALE_AVAILABLE = False
    logger.warning("Russian locale not available, using fallback")

def format_datetime_russian(dt: datetime) -> str:
    """Format datetime in Russian."""
    if LOCALE_AVAILABLE:
        return dt.strftime('%d %B %Y, %H:%M')
    
    months = [
        '', 'января', 'февраля', 'марта', 'апреля', 'мая',
        'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ]
    
    return f'{dt.day} {months[dt.month]} {dt.year}, {dt.hour:02d}:{dt.minute:02d}'

def format_duration(duration: timedelta) -> str:
    """Format duration in Russian."""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    return f'{hours} часов {minutes} минут'
