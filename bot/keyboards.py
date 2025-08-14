# ===== IMPORTS & DEPENDENCIES =====
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any

# ===== USER KEYBOARDS =====
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Returns the main menu keyboard for regular users."""
    keyboard = [
        [InlineKeyboardButton("🛒 خرید سرویس", callback_data="buy_service")],
        [InlineKeyboardButton("⚙️ سرویس‌های من", callback_data="my_services")],
        [
            InlineKeyboardButton("💰 کیف پول", callback_data="wallet"),
            InlineKeyboardButton("📞 پشتیبانی", callback_data="support")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_plans_keyboard(inbounds: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Dynamically builds a keyboard for service plans from inbounds."""
    keyboard = []
    for inbound in inbounds:
        # 'remark' is the plan name in x-ui panels
        plan_name = inbound.get("remark", f"پلن {inbound.get('id')}")
        # We create a callback_data like 'select_plan_1' where 1 is the inbound ID
        callback_data = f"select_plan_{inbound.get('id')}"
        keyboard.append([InlineKeyboardButton(f"🚀 {plan_name}", callback_data=callback_data)])
    
    # Add a back button to return to the main menu
    keyboard.append([InlineKeyboardButton("⬅️ بازگشت به منوی اصلی", callback_data="start_menu")])
    return InlineKeyboardMarkup(keyboard)


# ===== ADMIN KEYBOARDS =====
def get_admin_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Returns the main menu keyboard for admins."""
    keyboard = [
        [InlineKeyboardButton("🔧 مدیریت پنل‌ها", callback_data="admin_manage_panels")],
        [InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")],
        [InlineKeyboardButton("↩️ بازگشت به منوی کاربری", callback_data="start_menu")], # Changed to start_menu for consistency
    ]
    return InlineKeyboardMarkup(keyboard)

def get_panel_management_keyboard() -> InlineKeyboardMarkup:
    """Returns the keyboard for managing V2Ray panels."""
    keyboard = [
        [InlineKeyboardButton("➕ افزودن پنل جدید", callback_data="admin_add_panel")],
        [InlineKeyboardButton("📋 لیست پنل‌های ذخیره شده", callback_data="admin_list_panels")],
        [InlineKeyboardButton("⬅️ بازگشت به منوی ادمین", callback_data="admin_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)
