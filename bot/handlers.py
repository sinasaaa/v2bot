# ===== IMPORTS & DEPENDENCIES =====
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.config import settings
from crud import user_crud
from bot.keyboards import get_main_menu_keyboard, get_admin_main_menu_keyboard

# ===== START COMMAND HANDLER =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    db: Session = SessionLocal()
    try:
        is_admin_on_start = (user.id == settings.ADMIN_USER_ID)
        db_user = user_crud.create_user(db, telegram_user=user, is_admin=is_admin_on_start)
    finally:
        db.close()
        
    if db_user.is_admin:
        # Admin User Flow
        welcome_message = f"سلام ادمین {user.mention_html()}! 👋\n\nبه پنل مدیریت خوش آمدید."
        reply_markup = get_admin_main_menu_keyboard()
    else:
        # Regular User Flow
        welcome_message = f"سلام {user.mention_html()}! 👋\n\nبه ربات ما خوش آمدید."
        reply_markup = get_main_menu_keyboard()

    await update.message.reply_html(welcome_message, reply_markup=reply_markup)
