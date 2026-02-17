from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from app.core.config import settings

session = None
if settings.BOT_API_URL and settings.BOT_API_URL != "https://api.telegram.org":
    session = AiohttpSession(
        api=TelegramAPIServer.from_base(settings.BOT_API_URL),
        timeout=120,
    )

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session
)

dp = Dispatcher()


def get_bot() -> Bot:
    return bot


def get_dispatcher() -> Dispatcher:
    return dp
