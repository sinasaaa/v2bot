# ===== IMPORTS & DEPENDENCIES =====
import httpx
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

# ===== BASE PANEL MANAGER (Interface) =====
class BasePanelManager(ABC):
    """Abstract base class for all panel managers."""
    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.session: Optional[httpx.AsyncClient] = None

    @abstractmethod
    async def login(self) -> bool:
        """Logs into the panel and returns True on success, False otherwise."""
        pass

    @abstractmethod
    async def get_inbounds(self) -> List[Dict[str, Any]]:
        """Fetches a list of inbounds/plans from the panel."""
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(verify=False, timeout=10.0)
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()


# ===== MARZBAN PANEL MANAGER =====
class MarzbanPanel(BasePanelManager):
    """Manager for Marzban panels."""
    async def login(self) -> bool:
        if not self.session: return False
        try:
            api_url = self.api_url.rstrip('/')
            login_url = f"{api_url}/api/admin/token"
            data = {"username": self.username, "password": self.password}
            response = await self.session.post(login_url, data=data)

            if response.status_code == 200 and "access_token" in response.json():
                access_token = response.json()["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {access_token}"})
                return True
            return False
        except Exception:
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not self.session: return []
        # In Marzban, "users" act as templates/plans
        # This is a simplified logic, real logic might need to target specific user templates
        return [{"id": 1, "remark": "پلن پیش‌فرض مرزبان"}] # Placeholder

# ===== SANAEI (X-UI) PANEL MANAGER =====
class SanaeiPanel(BasePanelManager):
    """Manager for Sanaei (X-UI) panels."""
    async def login(self) -> bool:
        if not self.session: return False
        try:
            base_url = self.api_url.rstrip('/')
            login_url = f"{base_url}/login"
            data = {"username": self.username, "password": self.password}
            response = await self.session.post(login_url, data=data)
            
            is_successful_body = "success" in response.json() and response.json()["success"] is True
            has_cookie = "session" in response.cookies or "x-ui" in response.cookies
            
            return response.status_code == 200 and (is_successful_body or has_cookie)
        except Exception:
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not self.session: return []
        try:
            base_url = self.api_url.rstrip('/')
            inbounds_url = f"{base_url}/panel/api/inbounds/list"
            response = await self.session.get(inbounds_url)
            
            if response.status_code == 200 and response.json().get("success"):
                return response.json().get("obj", [])
            return []
        except Exception:
            return []

// ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
```**📖 توضیح تغییرات:**
*   **Context Manager (`__aenter__`, `__aexit__`)**: این یک روش بسیار حرفه‌ای در پایتون است. به ما اجازه می‌دهد تا با `async with` از `PanelManager` استفاده کنیم. این کار تضمین می‌کند که لاگین به صورت خودکار انجام شده و در انتها `session` بسته می‌شود.
*   **`get_inbounds`**: این متد جدید در هر کلاس پیاده‌سازی شده. برای `SanaeiPanel`، به آدرس واقعی API یعنی `/panel/api/inbounds/list` متصل می‌شود. برای `MarzbanPanel` فعلاً یک مقدار تستی برمی‌گردانیم چون منطق پلن در مرزبان متفاوت است و بعداً آن را تکمیل می‌کنیم.

#### **`bot/keyboards.py` (فайл ویرایش شده)**
یک تابع جدید برای ساخت کیبورد پلن‌ها اضافه می‌کنیم.

```python
// ===== IMPORTS & DEPENDENCIES =====
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any

# ===== USER KEYBOARDS =====
def get_main_menu_keyboard():
    # ... (code remains the same)
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
    
    # Add a back button
    keyboard.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="start_menu")])
    return InlineKeyboardMarkup(keyboard)

# ===== ADMIN KEYBOARDS =====
def get_admin_main_menu_keyboard():
    # ... (code remains the same)
    keyboard = [
        [InlineKeyboardButton("🔧 مدیریت پنل‌ها", callback_data="admin_manage_panels")],
        [InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")],
        [InlineKeyboardButton("↩️ بازگشت به منوی کاربری", callback_data="user_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)
# ... (rest of admin keyboards remain the same)
def get_panel_management_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ افزودن پنل جدید", callback_data="admin_add_panel")],
        [InlineKeyboardButton("📋 لیست پنل‌های ذخیره شده", callback_data="admin_list_panels")],
        [InlineKeyboardButton("⬅️ بازگشت به منوی ادمین", callback_data="admin_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)
