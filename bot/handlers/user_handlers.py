# ===== IMPORTS & DEPENDENCIES =====
from telegram import Update
from telegram.ext import ContextTypes

# ===== USER BUTTON HANDLER =====
async def user_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    # This will be expanded later
    if data == "buy_service":
        await query.edit_message_text(text="شما گزینه 'خرید سرویس' را انتخاب کردید. (این بخش در حال ساخت است)")
    elif data == "my_services":
        await query.edit_message_text(text="شما گزینه 'سرویس‌های من' را انتخاب کردید. (این بخش در حال ساخت است)")
    # ... other user options
