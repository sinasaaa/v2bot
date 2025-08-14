# ===== IMPORTS & DEPENDENCIES =====
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from core.database import SessionLocal
from crud import panel_crud
from services.panel_manager import get_panel_manager
from bot.keyboards import build_plans_keyboard, get_main_menu_keyboard

# ===== USER BUTTON HANDLER =====
async def user_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "buy_service":
        await query.edit_message_text(text="در حال دریافت لیست پلن‌ها از سرور...")
        
        db: Session = SessionLocal()
        try:
            # For now, let's use the first available panel
            panel = db.query(panel_crud.V2RayPanel).first()
            if not panel:
                await query.edit_message_text("متاسفانه در حال حاضر هیچ پنل فعالی برای فروش وجود ندارد.")
                return

            manager = get_panel_manager(
                panel_type=panel.panel_type.value,
                api_url=panel.api_url,
                username=panel.username,
                password=panel.password
            )

            if not manager:
                await query.edit_message_text("خطای داخلی در اتصال به پنل فروش.")
                return

            # Use the context manager for automatic login/logout
            async with manager as m:
                inbounds = await m.get_inbounds()

            if not inbounds:
                await query.edit_message_text("در حال حاضر هیچ پلن فعالی برای فروش یافت نشد.")
                return
            
            plans_keyboard = build_plans_keyboard(inbounds)
            await query.edit_message_text(
                "لطفا یکی از پلن‌های زیر را انتخاب کنید:",
                reply_markup=plans_keyboard
            )

        finally:
            db.close()

    elif data == "my_services":
        await query.edit_message_text(text="شما گزینه 'سرویس‌های من' را انتخاب کردید. (در حال ساخت)")
    
    elif data.startswith("select_plan_"):
        plan_id = data.split("_")[-1]
        await query.edit_message_text(f"شما پلن با شناسه {plan_id} را انتخاب کردید.\n\n(مرحله پرداخت و ساخت کانفیگ در حال ساخت است)")

    elif data == "start_menu":
        # This brings the user back to the main menu
        welcome_message = "به منوی اصلی بازگشتید."
        await query.edit_message_text(text=welcome_message, reply_markup=get_main_menu_keyboard())
