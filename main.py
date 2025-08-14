// ===== IMPORTS & DEPENDENCIES =====
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.config import settings
from bot.handlers import start, admin_panel  # Import the new handler

# ===== CONFIGURATION & CONSTANTS =====
# Initialize FastAPI app
app = FastAPI(title="V2Ray Sales Bot")

ptb_app: Application | None = None

# ===== CORE BUSINESS LOGIC =====
async def setup_telegram_bot():
    """Initializes the Telegram bot application and sets the webhook."""
    global ptb_app
    
    ptb_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(CommandHandler("admin", admin_panel)) # Add the admin handler
    
    webhook_url = f"{settings.WEBHOOK_URL}/telegram"
    await ptb_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook has been set to {webhook_url}")

async def shutdown_telegram_bot():
    """Cleans up the bot application on shutdown."""
    if ptb_app:
        print("Shutting down bot and removing webhook...")
        await ptb_app.bot.delete_webhook()

# ===== API ROUTES & CONTROLLERS =====
@app.on_event("startup")
async def on_startup():
    print("Application is starting up...")
    await setup_telegram_bot()

@app.on_event("shutdown")
async def on_shutdown():
    print("Application is shutting down...")
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
    return {"Hello": "World", "Project": "V2Ray Bot"}

# ===== INITIALIZATION & STARTUP =====
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
