# ===== IMPORTS & DEPENDENCIES =====
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from .decorators import admin_required
from core.database import SessionLocal
from crud import user_crud
from core.config import settings

# ===== CORE BUSINESS LOGIC (Bot Commands) =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    Greets the user, registers them in the database if they are new,
    and shows the main menu with inline buttons.
    """
    user = update.effective_user
    if not user:
        return

    db: Session = SessionLocal()
    try:
        is_admin = (user.id == settings.ADMIN_USER_ID)
        user_crud.create_user(db, telegram_user=user, is_admin=is_admin)
    finally:
        db.close()
    
    welcome_message = (
        f"سلام {user.mention_html()}! 👋\n\n"
        "به ربات فروش کانفیگ خوش آمدید.\n"
        "برای شروع، از دکمه‌های زیر استفاده کنید."
    )

    # --- Define the main menu keyboard ---
    keyboard = [
        [InlineKeyboardButton("🛒 خرید سرویس", callback_data="buy_service")],
        [InlineKeyboardButton("⚙️ سرویس‌های من", callback_data="my_services")],
        [
            InlineKeyboardButton("💰 کیف پول", callback_data="wallet"),
            InlineKeyboardButton("📞 پشتیبانی", callback_data="support")
        ],
    ]
    
    # Create the InlineKeyboardMarkup object
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with the keyboard
    await update.message.reply_html(welcome_message, reply_markup=reply_markup)


@admin_required
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /admin command.
    Shows the admin control panel. Access is restricted to admins.
    """
    user = update.effective_user
    admin_message = (
        f"سلام ادمین {user.mention_html()}!\n\n"
        "به پنل مدیریت خوش آمدید. در اینجا می‌توانید ربات را مدیریت کنید."
    )
    await update.message.reply_html(admin_message)
