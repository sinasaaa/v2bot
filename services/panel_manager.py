# ===== IMPORTS & DEPENDENCIES =====
import httpx
from abc import ABC, abstractmethod

# ===== BASE PANEL MANAGER (Interface) =====
class BasePanelManager(ABC):
    """Abstract base class for all panel managers."""
    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = httpx.AsyncClient(verify=False) # verify=False for self-signed certs

    @abstractmethod
    async def login(self) -> bool:
        """Logs into the panel and returns True on success, False otherwise."""
        pass

    async def close_session(self):
        """Closes the httpx session."""
        await self.session.aclose()

# ===== MARZBAN PANEL MANAGER =====
class MarzbanPanel(BasePanelManager):
    """Manager for Marzban panels."""
    async def login(self) -> bool:
        try:
            login_url = f"{self.api_url}/api/admin/token"
            data = {"username": self.username, "password": self.password}
            response = await self.session.post(login_url, data=data)

            if response.status_code == 200 and "access_token" in response.json():
                access_token = response.json()["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {access_token}"})
                return True
            return False
        except Exception as e:
            print(f"[Marzban Login Error] {e}")
            return False

# ===== SANAEI (X-UI) PANEL MANAGER =====
class SanaeiPanel(BasePanelManager):
    """Manager for Sanaei (X-UI) panels."""
    async def login(self) -> bool:
        try:
            login_url = f"{self.api_url}/login"
            data = {"username": self.username, "password": self.password}
            response = await self.session.post(login_url, data=data)
            
            # Successful login in x-ui often results in a cookie and a 200 status code
            if response.status_code == 200 and "session" in response.cookies:
                return True
            return False
        except Exception as e:
            print(f"[Sanaei Login Error] {e}")
            return False

# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> BasePanelManager | None:
    """Factory function to get the correct panel manager instance."""
    panel_classes = {
        "marzban": MarzbanPanel,
        "sanaei": SanaeiPanel,
    }
    manager_class = panel_classes.get(panel_type)
    if manager_class:
        return manager_class(api_url, username, password)
    return None
