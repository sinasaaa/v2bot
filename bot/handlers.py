# ===== IMPORTS & DEPENDENCIES =====
from telegram import Update
from telegram.ext import ContextTypes

# ===== CORE BUSINESS LOGIC (Bot Commands) =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    Greets the user and shows the main menu.
    """
    user = update.effective_user
    if not user:
        return # Should not happen

    # A friendly welcome message
    welcome_message = (
        f"سلام {user.mention_html()}! 👋\n\n"
        "به ربات فروش کانفیگ خوش آمدید.\n"
        "برای شروع، از دکمه‌های زیر استفاده کنید."
    )
    
    # Here we will later add a keyboard with buttons
    await update.message.reply_html(welcome_message)
