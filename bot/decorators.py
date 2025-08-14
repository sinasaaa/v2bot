// ===== IMPORTS & DEPENDENCIES =====
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from core.database import SessionLocal
from crud import user_crud
from core.config import settings

# ===== DECORATORS =====
def admin_required(func):
    """
    A decorator to restrict access to a handler to admins only.
    It checks the `is_admin` flag in the database.
    """
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return

        db: Session = SessionLocal()
        try:
            # The main admin from settings ALWAYS has access.
            is_main_admin = (user.id == settings.ADMIN_USER_ID)
            # Check other admins from the database.
            is_db_admin = user_crud.is_user_admin(db, telegram_id=user.id)

            if not (is_main_admin or is_db_admin):
                print(f"🚫 Unauthorized access attempt by user {user.id} ({user.username}).")
                await update.message.reply_text("شما اجازه دسترسی به این دستور را ندارید.")
                return
        finally:
            db.close()

        print(f"✅ Admin access granted to user {user.id} ({user.username}).")
        return await func(update, context, *args, **kwargs)

    return wrapped
