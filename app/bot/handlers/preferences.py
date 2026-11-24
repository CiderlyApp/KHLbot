"""Notification and favorite-team preferences."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.bot.keyboards import teams_keyboard
from app.services.users import enable_notifications, choose_team, register_user

router = Router()
TEAMS = ["Адмирал", "Ак Барс", "Амур", "Авангард", "Автомобилист", "Барыс", "Динамо Минск", "Динамо Москва", "Лада", "Локомотив", "Металлург", "Нефтехимик", "Салават Юлаев", "Северсталь", "Сибирь", "СКА", "Сочи", "Спартак", "Торпедо", "Трактор", "ЦСКА", "Шанхайские Драконы"]

@router.message(Command("subscribe"))
async def subscribe(message: Message):
    register_user(message.from_user)
    enable_notifications(message.from_user.id, True)
    await message.answer("🔔 Уведомления включены. По умолчанию — обо всех командах. Выбери любимую команду через /team, чтобы получать уведомления только о её матчах.")

@router.message(Command("unsubscribe"))
async def unsubscribe(message: Message):
    register_user(message.from_user)
    enable_notifications(message.from_user.id, False)
    await message.answer("Уведомления выключены.")

@router.message(Command("team"))
async def team(message: Message):
    register_user(message.from_user)
    await message.answer("Выбери команду:", reply_markup=teams_keyboard(TEAMS))

@router.callback_query(F.data == "notifications:on")
async def enable_callback(callback: CallbackQuery):
    register_user(callback.from_user)
    enable_notifications(callback.from_user.id, True)
    await callback.answer("Уведомления включены")
    await callback.message.answer("🔔 Уведомления включены. Отключить — /unsubscribe")

@router.callback_query(F.data == "team:choose")
async def choose_callback(callback: CallbackQuery):
    await callback.message.answer("Выбери команду:", reply_markup=teams_keyboard(TEAMS))
    await callback.answer()

@router.callback_query(F.data.startswith("team:set:"))
async def set_team_callback(callback: CallbackQuery):
    register_user(callback.from_user)
    value = callback.data.split(":", 2)[2]
    choose_team(callback.from_user.id, None if value == "all" else value)
    await callback.answer("Фильтр сохранён")
    await callback.message.answer("Буду присылать уведомления: " + ("по всем командам" if value == "all" else f"о матчах команды {value}"))
