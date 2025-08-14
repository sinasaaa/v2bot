// ===== IMPORTS & DEPENDENCIES =====
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from core.config import settings

# This would ideally interact with a database session, which we will set up later.
# For now, let's assume we have a way to check if a user is an admin.
# We'll check against the ADMIN_USER_ID from settings.

# ===== DECORATORS =====
def admin_required(func):
    """
    A decorator to restrict access to a handler to admins only.
    """
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return  # Should not happen

        # For now, we only check the main admin ID from settings.
        # Later, we will enhance this to check the `is_admin` flag from the database.
        if user.id != settings.ADMIN_USER_ID:
            print(f"🚫 Unauthorized access attempt by user {user.id} ({user.username}).")
            await update.message.reply_text("شما اجازه دسترسی به این دستور را ندارید.")
            return

        print(f"✅ Admin access granted to user {user.id} ({user.username}).")
        return await func(update, context, *args, **kwargs)

    return wrapped
