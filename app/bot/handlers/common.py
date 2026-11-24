"""Start and help commands."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from app.bot.keyboards import main_keyboard
from app.services.users import register_user

router = Router()

HELP = (
    "<b>KHLbot — хоккей рядом</b>\n\n"
    "/today — матчи сегодня\n/tomorrow — матчи завтра\n/week — ближайшие 7 дней\n"
    "/subscribe — включить уведомления\n/unsubscribe — выключить уведомления\n"
    "/team — выбрать любимую команду\n/help — помощь"
)

@router.message(CommandStart())
async def start(message: Message):
    register_user(message.from_user)
    await message.answer(HELP, reply_markup=main_keyboard())

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(HELP, reply_markup=main_keyboard())

@router.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.message.edit_text(HELP, reply_markup=main_keyboard())
    await callback.answer()
