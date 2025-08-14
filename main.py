# ===== IMPORTS & DEPENDENCIES =====
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.config import settings
from core.database import engine
from models import user as user_model
from bot.handlers import start, admin_panel

# ===== CONFIGURATION & CONSTANTS =====
# Create all database tables
user_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="V2Ray Sales Bot")
ptb_app: Application | None = None

# ===== CORE BUSINESS LOGIC =====
async def setup_telegram_bot():
    """Initializes the Telegram bot application, sets the webhook, and prepares it for running."""
    global ptb_app
    
    ptb_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(CommandHandler("admin", admin_panel))
    
    # ===> THE CRITICAL FIX - PART 1 <===
    # Initialize the application to prepare it for running
    await ptb_app.initialize()
    
    # Set the webhook
    webhook_url = f"{settings.WEBHOOK_URL}/telegram"
    await ptb_app.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
    print(f"Webhook has been set to {webhook_url}")

async def shutdown_telegram_bot():
    """Cleans up the bot application on shutdown."""
    if ptb_app:
        print("Shutting down bot application...")
        # ===> THE CRITICAL FIX - PART 2 <===
        # Shutdown the application gracefully
        await ptb_app.shutdown()
        # Note: Deleting the webhook is optional and often not needed. 
        # await ptb_app.bot.delete_webhook()

# ===== API ROUTES & CONTROLLERS =====
@app.on_event("startup")
async def on_startup():
    """Actions to perform on application startup."""
    print("Application is starting up...")
    await setup_telegram_bot()

@app.on_event("shutdown")
async def on_shutdown():
    """Actions to perform on application shutdown."""
    print("Application is shutting down...")
    await shutdown_telegram_bot()

@app.post("/telegram")
async def telegram_webhook(request: Request):
    """
    This endpoint is the webhook for Telegram.
    It receives updates from Telegram and processes them.
    """
    if ptb_app and ptb_app.initialized:
        update_data = await request.json()
        update = Update.de_json(data=update_data, bot=ptb_app.bot)
        await ptb_app.process_update(update)
        return {"status": "ok"}
    return {"status": "bot not initialized"}

@app.get("/")
def read_root():
    """A simple health check endpoint."""
    return {"Hello": "World", "Project": "V2Ray Bot"}

# ===== INITIALIZATION & STARTUP =====
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
