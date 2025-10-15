"""Handlers package."""
from aiogram import Router
from handlers import start, menu, streamers

def get_routers() -> list[Router]:
    """Get all routers."""
    return [
        start.router,
        menu.router,
        streamers.router
    ]
