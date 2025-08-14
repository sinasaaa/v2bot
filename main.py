# ===== IMPORTS & DEPENDENCIES =====
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from core.config import settings
from core.database import engine
from models import user as user_model
from models import panel as panel_model

from bot.handlers.common_handlers import start
from bot.handlers.user_handlers import user_button_handler
# Import all admin handlers including conversation parts
from bot.handlers.admin_handlers import (
    admin_button_handler,
    start_add_panel_conversation,
    receive_panel_name,
    receive_panel_type,
    receive_panel_url,
    receive_panel_username,
    receive_panel_password,
    cancel_conversation,
    PANEL_NAME,
    PANEL_TYPE,
    PANEL_URL,
    PANEL_USERNAME,
    PANEL_PASSWORD,
)

# ===== CONFIGURATION & CONSTANTS =====
user_model.Base.metadata.create_all(bind=engine)
panel_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="V2Ray Sales Bot")
ptb_app: Application | None = None

# ===== CORE BUSINESS LOGIC =====
async def setup_telegram_bot():
    global ptb_app
    ptb_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    await ptb_app.initialize()

    # --- Setup Conversation Handler for adding panels ---
    add_panel_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_panel_conversation, pattern='^admin_add_panel$')],
        states={
            PANEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_name)],
            PANEL_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_type)],
            PANEL_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_url)],
            PANEL_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_username)],
            PANEL_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
    )

    # Register handlers
    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(add_panel_conv_handler) # Add conversation handler
    
    # The generic button handlers must be added AFTER the conversation handler
    ptb_app.add_handler(CallbackQueryHandler(admin_button_handler, pattern='^admin_.*$'))
    ptb_app.add_handler(CallbackQueryHandler(user_button_handler, pattern='^(?!admin_).*$'))

    webhook_url = f"{settings.WEBHOOK_URL}/telegram"
    await ptb_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook has been set to {webhook_url}")

# ... (Rest of main.py remains the same) ...
async def shutdown_telegram_bot():
    if ptb_app:
        await ptb_app.shutdown()

@app.on_event("startup")
async def on_startup():
    await setup_telegram_bot()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown_telegram_bot()

@app.post("/telegram")
async def telegram_webhook(request: Request):
    if ptb_app:
        update_data = await request.json()
        update = Update.de_json(data=update_data, bot=ptb_app.bot)
        await ptb_app.process_update(update)
        return {"status": "ok"}
    return {"status": "bot not initialized"}

@app.get("/")
def read_root():
    return {"Project": "V2Ray Bot"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
