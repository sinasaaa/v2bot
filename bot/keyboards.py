# ===== IMPORTS & DEPENDENCIES =====
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ===== USER KEYBOARDS =====
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 خرید سرویس", callback_data="buy_service")],
        [InlineKeyboardButton("⚙️ سرویس‌های من", callback_data="my_services")],
        [
            InlineKeyboardButton("💰 کیف پول", callback_data="wallet"),
            InlineKeyboardButton("📞 پشتیبانی", callback_data="support")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== ADMIN KEYBOARDS =====
def get_admin_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔧 مدیریت پنل‌ها", callback_data="admin_manage_panels")],
        [InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")],
        [InlineKeyboardButton("↩️ بازگشت به منوی کاربری", callback_data="user_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_panel_management_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ افزودن پنل جدید", callback_data="admin_add_panel")],
        [InlineKeyboardButton("📋 لیست پنل‌های ذخیره شده", callback_data="admin_list_panels")],
        [InlineKeyboardButton("⬅️ بازگشت به منوی ادمین", callback_data="admin_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)
