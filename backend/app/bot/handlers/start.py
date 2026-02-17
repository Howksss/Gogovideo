from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, FSInputFile
from app.db.base import AsyncSessionLocal
from app.db.crud import UserCRUD
from app.core.config import settings

router = Router()

PROMO_VIDEO_PATH = "/app/promo.mp4"


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with AsyncSessionLocal() as db:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        referred_by = None

        if args and args[0].startswith("ref_"):
            try:
                ref_id = int(args[0].replace("ref_", ""))
                if ref_id != message.from_user.id:
                    referred_by = ref_id
            except ValueError:
                pass

        user = await UserCRUD.get_or_create(
            db,
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            referred_by=referred_by
        )

        bot_me = await message.bot.me()
        bot_username = bot_me.username

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Открыть GoGoVideo",
                web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )],
        ])

        welcome_text = (
            f"<b>GoGoVideo — медиа в Telegram без тормозов</b>\n\n"
            f"Перешли сюда видео, фото или голосовое — открой веб-приложение и смотри на высокой скорости.\n\n"
            f"Нужно отправить видео? Загрузи через веб-приложение, потом набери "
            f"<code>@{bot_username}</code> в любом чате — улетит за секунду.\n\n"
            f"3 ГБ/день на загрузку, 3 ГБ/день на просмотр. Зови друзей — лимит растёт.\n\n"
            f"/help — справка"
        )

        if referred_by and settings.ENABLE_REFERRAL:
            bonus_gb = settings.REFERRAL_BONUS_INVITEE_MB / 1024
            welcome_text += f"\n\n🎉 Реферальный бонус активирован: +{bonus_gb:.0f} ГБ к дневным лимитам!"

        try:
            video_file = FSInputFile(PROMO_VIDEO_PATH)
            await message.answer_video(
                video=video_file,
                caption=welcome_text,
                reply_markup=keyboard,
            )
        except Exception:
            await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    bot_username = (await message.bot.me()).username

    help_text = (
        f"<b>Частые вопросы</b>\n\n"

        f"<b>Как смотреть видео без тормозов?</b>\n"
        f"Перешли боту — открой приложение — смотри. "
        f"Работает с видео, фото, голосовыми, аудио и альбомами.\n\n"

        f"<b>Как отправить видео быстро?</b>\n"
        f"Загрузи через приложение, потом в любом чате пиши "
        f"<code>@{bot_username}</code> — выбираешь видео, оно улетает за секунду. "
        f"Заново ничего грузить не надо.\n\n"

        f"<b>Мои файлы где-то хранятся?</b>\n"
        f"На серверах Telegram. Бот ничего у себя не держит, всё стримится напрямую.\n\n"

        f"<b>Какие лимиты?</b>\n"
        f"3 ГБ/день загрузка, 3 ГБ/день просмотр. Сброс в 00:00 МСК.\n\n"

        f"<b>Как получить больше?</b>\n"
        f"Зови друзей. Тебе +0.2 ГБ за каждого, другу +1 ГБ. "
        f"До 10 друзей = +2 ГБ сверху. Ссылка в разделе «Рефералы» в приложении.\n\n"

        f"<b>Это безопасно?</b>\n"
        f"Авторизация через Telegram. Чужие файлы не видны, доступ только к своим.\n\n"

        f"За любой помощью можно обращаться к @Howksss"
    )

    await message.answer(help_text)
