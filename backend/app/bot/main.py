import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from app.bot.bot_instance import bot, dp
from app.bot.handlers import start, inline, admin, forward
from app.core.logger import logger
from app.core.config import settings
from app.db.base import close_db


async def set_bot_commands(bot: Bot):
    commands_list = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="help", description="Справка"),
    ]
    await bot.set_my_commands(commands_list)


async def main():
    logger.info("Starting Telegram Bot...")

    dp.include_router(start.router)
    dp.include_router(inline.router)
    dp.include_router(admin.router)
    dp.include_router(forward.router)

    await set_bot_commands(bot)

    await bot.set_my_description(
        f"{settings.APP_NAME} — храни и смотри медиа из Telegram на максимальной скорости"
    )
    await bot.set_my_short_description(
        "Быстрое хранилище медиа для Telegram"
    )

    logger.info("Bot configured successfully")

    try:
        logger.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=["message", "inline_query", "chosen_inline_result", "callback_query"])
    except Exception as e:
        logger.error(f"Error in bot polling: {e}")
    finally:
        await bot.session.close()
        await close_db()
        logger.info("Database connections closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
