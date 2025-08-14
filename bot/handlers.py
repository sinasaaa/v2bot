// ===== IMPORTS & DEPENDENCIES =====
from telegram import Update
from telegram.ext import ContextTypes
from .decorators import admin_required

# Note: We will need a database session to save users. 
# This will be added in the next step. For now, we just show the logic.

# ===== CORE BUSINESS LOGIC (Bot Commands) =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    Greets the user, registers them in the database if they are new,
    and shows the main menu.
    """
    user = update.effective_user
    if not user:
        return

    #
    # --- DATABASE LOGIC (to be implemented with a real session) ---
    # 1. Check if user with `user.id` exists in the database.
    # 2. If not, create a new User entry:
    #    new_user = User(
    #        telegram_id=user.id,
    #        first_name=user.first_name,
    #        last_name=user.last_name,
    #        username=user.username,
    #        is_admin=(user.id == settings.ADMIN_USER_ID) # Set admin status on first join
    #    )
    #    db.add(new_user)
    #    db.commit()
    #    print(f"New user {user.username} registered.")
    # -----------------------------------------------------------------
    #
    
    welcome_message = (
        f"سلام {user.mention_html()}! 👋\n\n"
        "به ربات فروش کانفیگ خوش آمدید.\n"
        "برای شروع، از دکمه‌های زیر استفاده کنید."
    )
    
    await update.message.reply_html(welcome_message)


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
    # Later, we will add admin-specific buttons here.
    await update.message.reply_html(admin_message)
