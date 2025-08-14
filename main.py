# ===== IMPORTS & DEPENDENCIES =====
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from core.config import settings
from core.database import engine
from models import user as user_model
from models import panel as panel_model

from bot.handlers.common_handlers import start
from bot.handlers.user_handlers import user_button_handler
from bot.handlers.admin_handlers import admin_button_handler

# ===== CONFIGURATION & CONSTANTS =====
user_model.Base.metadata.create_all(bind=engine)
panel_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="V2Ray Sales Bot")
ptb_app: Application | None = None

# ===== CORE BUSINESS LOGIC =====
async def setup_telegram_bot():
    """Initializes the Telegram bot application, runs post-init tasks, and sets the webhook."""
    global ptb_app
    
    ptb_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # ==>> THE FIX IS HERE <<==
    # Explicitly initialize the application
    await ptb_app.initialize()

    # Register handlers
    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(CallbackQueryHandler(admin_button_handler, pattern='^admin_.*$'))
    ptb_app.add_handler(CallbackQueryHandler(user_button_handler, pattern='^(?!admin_).*$'))

    # Set the webhook AFTER initialization
    webhook_url = f"{settings.WEBHOOK_URL}/telegram"
    await ptb_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook has been set to {webhook_url}")

async def shutdown_telegram_bot():
    """Shuts down the application and performs cleanup."""
    if ptb_app:
        # Explicitly shutdown the application
        await ptb_app.shutdown()

@app.on_event("startup")
async def on_startup():
    await setup_telegram_bot()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown_telegram_bot()

@app.post("/telegram")
async def telegram_webhook(request: Request):
    """Processes incoming Telegram updates."""
    if ptb_app:
        update_data = await request.json()
        update = Update.de_json(data=update_data, bot=ptb_app.bot)
        # The application is already initialized, so we can process the update
        await ptb_app.process_update(update)
        return {"status": "ok"}
    return {"status": "bot not initialized"}

@app.get("/")
def read_root():
    return {"Project": "V2Ray Bot"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
