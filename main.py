# ===== IMPORTS & DEPENDENCIES =====
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from core.config import settings
from core.database import engine
from models import user as user_model
from models import panel as panel_model # Import new panel model

# Import handlers from the new structure
from bot.handlers.common_handlers import start
from bot.handlers.user_handlers import user_button_handler
from bot.handlers.admin_handlers import admin_button_handler

# ===== CONFIGURATION & CONSTANTS =====
# Create all database tables for all models
user_model.Base.metadata.create_all(bind=engine)
panel_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="V2Ray Sales Bot")
ptb_app: Application | None = None

# ===== CORE BUSINESS LOGIC =====
async def setup_telegram_bot():
    global ptb_app
    ptb_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    ptb_app.add_handler(CommandHandler("start", start))
    
    # We use regex to route callbacks to the correct handler
    ptb_app.add_handler(CallbackQueryHandler(admin_button_handler, pattern='^admin_.*$'))
    ptb_app.add_handler(CallbackQueryHandler(user_button_handler, pattern='^(?!admin_).*$'))

    webhook_url = f"{settings.WEBHOOK_URL}/telegram"
    await ptb_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook has been set to {webhook_url}")

# ... (Rest of main.py remains the same: shutdown, on_startup, etc.) ...
async def shutdown_telegram_bot():
    if ptb_app:
        await ptb_app.bot.delete_webhook()

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

@app.get("/")
def read_root():
    return {"Project": "V2Ray Bot"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
