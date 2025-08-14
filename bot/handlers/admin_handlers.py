# ===== IMPORTS & DEPENDENCIES =====
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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

# ===== CONVERSATION STATES =====
# Define states for the conversation. Each state represents a step in the conversation.
(
    PANEL_NAME,
    PANEL_TYPE,
    PANEL_URL,
    PANEL_USERNAME,
    PANEL_PASSWORD,
    CONFIRM_PANEL,
) = range(6)


# ===== HELPER FUNCTIONS =====
async def start_add_panel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to add a new panel."""
    query = update.callback_query
    await query.answer()
    
    # Initialize an empty dictionary to store panel data during the conversation
    context.user_data['new_panel'] = {}
    
    await query.edit_message_text(
        "شروع فرآیند افزودن پنل جدید...\n\n"
        "لطفا یک **نام منحصر به فرد** برای این پنل وارد کنید (مثلا: پنل اصلی آلمان). این نام فقط برای نمایش در ربات است.\n\n"
        "برای لغو در هر زمان، دستور /cancel را ارسال کنید."
    )
    return PANEL_NAME


async def receive_panel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the panel name and asks for the panel type."""
    panel_name = update.message.text
    context.user_data['new_panel']['name'] = panel_name

    # Create a reply keyboard for panel types
    panel_type_keyboard = [[panel.value for panel in PanelType]]
    
    await update.message.reply_text(
        f"نام پنل: '{panel_name}' ذخیره شد.\n\n"
        "حالا **نوع پنل** را از کیبورد زیر انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(panel_type_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return PANEL_TYPE


async def receive_panel_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives panel type and asks for the URL."""
    panel_type_str = update.message.text
    try:
        panel_type = PanelType(panel_type_str)
        context.user_data['new_panel']['type'] = panel_type
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
    """Receives panel URL and asks for the username."""
    context.user_data['new_panel']['url'] = update.message.text
    await update.message.reply_text(
        "آدرس پنل ذخیره شد.\n\n"
        "حالا **نام کاربری (username)** برای ورود به پنل را وارد کنید:"
    )
    return PANEL_USERNAME


async def receive_panel_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives username and asks for the password."""
    context.user_data['new_panel']['username'] = update.message.text
    await update.message.reply_text(
        "نام کاربری ذخیره شد.\n\n"
        "حالا **رمز عبور (password)** برای ورود به پنل را وارد کنید:"
    )
    return PANEL_PASSWORD


async def receive_panel_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives password, saves the panel, and ends the conversation."""
    context.user_data['new_panel']['password'] = update.message.text
    
    panel_data = context.user_data['new_panel']
    
    # TODO: Add a step to test the connection to the panel API before saving.
    
    db: Session = SessionLocal()
    try:
        panel_crud.create_panel(
            db=db,
            name=panel_data['name'],
            panel_type=panel_data['type'],
            api_url=panel_data['url'],
            username=panel_data['username'],
            password=panel_data['password'],
        )
        await update.message.reply_text(
            f"✅ پنل '{panel_data['name']}' با موفقیت در دیتابیس ذخیره شد.",
            reply_markup=get_admin_main_menu_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"❌ خطایی در ذخیره پنل رخ داد: {e}")
    finally:
        db.close()
        del context.user_data['new_panel']

    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    if 'new_panel' in context.user_data:
        del context.user_data['new_panel']
        
    await update.message.reply_text(
        "فرآیند افزودن پنل لغو شد.",
        reply_markup=get_admin_main_menu_keyboard()
    )
    return ConversationHandler.END

# ===== ADMIN BUTTON HANDLER =====
async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin_manage_panels":
        await query.edit_message_text(
            text="لطفا یکی از گزینه‌های زیر را برای مدیریت پنل‌ها انتخاب کنید:",
            reply_markup=get_panel_management_keyboard()
        )
    elif data == "admin_menu":
        await query.edit_message_text(
            text="شما به منوی اصلی ادمین بازگشتید.",
            reply_markup=get_admin_main_menu_keyboard()
        )
    # Note: The 'admin_add_panel' is now handled by the ConversationHandler entry point
