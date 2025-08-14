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
        # We don't login here automatically, login is called by the specific implementation if needed
        # This makes the context manager more flexible.
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session and not self.session.is_closed:
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
        if not await self.login(): return []
        # In Marzban, "users" can act as templates/plans
        # This is a simplified logic, real logic might need to target specific user templates
        # For now, returning a placeholder
        print("Marzban get_inbounds is currently a placeholder.")
        return [{"id": 1, "remark": "پلن پیش‌فرض مرزبان"}] 


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
            
            is_successful_body = False
            try:
                if response.json().get("success") is True:
                    is_successful_body = True
            except Exception:
                pass

            has_cookie = "session" in response.cookies or "x-ui" in response.cookies
            
            if response.status_code == 200 and (is_successful_body or has_cookie):
                return True
            return False
        except Exception:
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not await self.login(): return []
        
        try:
            base_url = self.api_url.rstrip('/')
            inbounds_url = f"{base_url}/panel/api/inbounds/list"
            response = await self.session.get(inbounds_url)
            
            if response.status_code == 200 and response.json().get("success"):
                return response.json().get("obj", [])
            return []
        except Exception:
            return []

# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = {
        "marzban": MarzbanPanel,
        "sanaei": SanaeiPanel,
    }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
