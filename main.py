// ===== IMPORTS & DEPENDENCIES =====
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.config import settings
from core.database import engine
from models import user as user_model # Import the user model
from bot.handlers import start, admin_panel

# ===== CONFIGURATION & CONSTANTS =====
# Create all database tables
# This line checks if the 'users' table exists, and if not, creates it.
user_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="V2Ray Sales Bot")
ptb_app: Application | None = None

# ... (Rest of the file remains the same) ...

// ===== API ROUTES & CONTROLLERS =====
@app.on_event("startup")
async def on_startup():
    """Actions to perform on application startup."""
    print("Application is starting up...")
    await setup_telegram_bot()

# ... (The rest of the file from here is identical to the previous version) ...

# NOTE: No other changes are needed in this file for now.
# We are simply adding the table creation line at the top.
# The full code is provided for clarity.

// --- FULL main.py for clarity ---
async def setup_telegram_bot():
    global ptb_app
    ptb_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(CommandHandler("admin", admin_panel))
    webhook_url = f"{settings.WEBHOOK_URL}/telegram"
    await ptb_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook has been set to {webhook_url}")

async def shutdown_telegram_bot():
    if ptb_app:
        print("Shutting down bot and removing webhook...")
        await ptb_app.bot.delete_webhook()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
