# ===== IMPORTS & DEPENDENCIES =====
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from sqlalchemy.orm import Session

from bot.keyboards import get_panel_management_keyboard, get_admin_main_menu_keyboard
from core.database import SessionLocal
from crud import panel_crud
from models.panel import PanelType
from services.panel_manager import get_panel_manager

# ===== CONVERSATION STATES =====
(
    PANEL_NAME,
    PANEL_TYPE,
    PANEL_URL,
    PANEL_USERNAME,
    PANEL_PASSWORD,
) = range(5)


# ===== HELPER FUNCTIONS for Conversation =====
async def start_add_panel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    context.user_data['new_panel'] = {}
    
    await query.edit_message_text(
        "شروع فرآیند افزودن پنل جدید...\n\n"
        "لطفا یک **نام منحصر به فرد** برای این پنل وارد کنید (مثلا: پنل اصلی آلمان). این نام فقط برای نمایش در ربات است.\n\n"
        "برای لغو در هر زمان، دستور /cancel را ارسال کنید.",
        parse_mode=ParseMode.MARKDOWN
    )
    return PANEL_NAME


async def receive_panel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    panel_name = update.message.text
    context.user_data['new_panel']['name'] = panel_name

    panel_type_keyboard = [[panel.value for panel in PanelType]]
    
    await update.message.reply_text(
        f"نام پنل: '{panel_name}' ذخیره شد.\n\n"
        "حالا **نوع پنل** را از کیبورد زیر انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(panel_type_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return PANEL_TYPE


async def receive_panel_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    panel_type_str = update.message.text
    try:
        panel_type = PanelType(panel_type_str)
        context.user_data['new_panel']['panel_type'] = panel_type
        
        await update.message.reply_text(
            f"نوع پنل: '{panel_type.value}' ذخیره شد.\n\n"
            "حالا **آدرس کامل (URL)** پنل را وارد کنید (مثلا: https://panel.example.com):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PANEL_URL
    except ValueError:
        await update.message.reply_text("نوع پنل نامعتبر است. لطفا یکی از گزینه‌های روی کیبورد را انتخاب کنید.")
        return PANEL_TYPE


async def receive_panel_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_panel']['api_url'] = update.message.text
    
    await update.message.reply_text(
        "آدرس پنل ذخیره شد.\n\n"
        "حالا **نام کاربری (username)** برای ورود به پنل را وارد کنید:"
    )
    return PANEL_USERNAME


async def receive_panel_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_panel']['username'] = update.message.text
    await update.message.reply_text(
        "نام کاربری ذخیره شد.\n\n"
        "حالا **رمز عبور (password)** برای ورود به پنل را وارد کنید:"
    )
    return PANEL_PASSWORD


async def receive_panel_password_and_validate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_panel']['password'] = update.message.text
    panel_data = context.user_data['new_panel']
    
    await update.message.reply_text("اطلاعات دریافت شد. در حال تلاش برای اتصال به پنل...")

    panel_manager = get_panel_manager(
        panel_type=panel_data['panel_type'].value,
        api_url=panel_data['api_url'],
        username=panel_data['username'],
        password=panel_data['password'],
    )
    
    if not panel_manager:
        await update.message.reply_text("❌ خطای داخلی: مدیر پنل برای این نوع یافت نشد.")
        if 'new_panel' in context.user_data: del context.user_data['new_panel']
        return ConversationHandler.END

    login_successful = await panel_manager.login()

    if not login_successful:
        await update.message.reply_text(
            "❌ **اتصال به پنل ناموفق بود.**\n\n"
            "لطفا از صحت آدرس، نام کاربری و رمز عبور اطمینان حاصل کرده و دوباره تلاش کنید.",
            reply_markup=get_panel_management_keyboard()
        )
        if 'new_panel' in context.user_data: del context.user_data['new_panel']
        return ConversationHandler.END
        
    await update.message.reply_text("✅ اتصال
