# ===== IMPORTS & DEPENDENCIES =====
# ... (other imports remain the same)
from services.panel_manager import get_panel_manager

# ... (rest of the file until receive_panel_password remains the same)

async def receive_panel_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives password, tests connection, saves the panel, and ends conversation."""
    context.user_data['new_panel']['password'] = update.message.text
    
    panel_data = context.user_data['new_panel']
    
    await update.message.reply_text("اطلاعات دریافت شد. در حال تلاش برای اتصال به پنل...")

    # --- Test Connection ---
    panel_manager = get_panel_manager(
        panel_type=panel_data['type'].value,
        api_url=panel_data['url'],
        username=panel_data['username'],
        password=panel_data['password'],
    )
    
    if not panel_manager:
        await update.message.reply_text("❌ خطای داخلی: مدیر پنل برای این نوع یافت نشد.")
        return ConversationHandler.END

    login_successful = await panel_manager.login()
    await panel_manager.close_session() # Close the session after login test

    if not login_successful:
        await update.message.reply_text(
            "❌ اتصال به پنل با موفقیت انجام نشد. لطفا اطلاعات را بررسی کرده و دوباره تلاش کنید.",
            reply_markup=get_admin_main_menu_keyboard()
        )
        del context.user_data['new_panel']
        return ConversationHandler.END
        
    # --- Save to DB if connection is successful ---
    await update.message.reply_text("✅ اتصال با موفقیت برقرار شد. در حال ذخیره در دیتابیس...")
    
    db: Session = SessionLocal()
    try:
        panel_crud.create_panel(
            db=db,
            name=panel_data['name'],
            panel_type=panel_data['type'],
            api_url=panel_data['url'],
            username=panel_data['username'],
            password=panel_data['password'],
        )
        await update.message.reply_text(
            f"✅ پنل '{panel_data['name']}' با موفقیت در دیتابیس ذخیره شد.",
            reply_markup=get_admin_main_menu_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"❌ خطایی در ذخیره پنل رخ داد: {e}")
    finally:
        db.close()
        del context.user_data['new_panel']

    return ConversationHandler.END

# ... (rest of the file remains the same)
