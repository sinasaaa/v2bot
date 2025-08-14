# ===== IMPORTS & DEPENDENCIES =====
import httpx
from abc import ABC, abstractmethod
from typing import Optional

# ===== BASE PANEL MANAGER (Interface) =====
class BasePanelManager(ABC):
    """Abstract base class for all panel managers."""
    def __init__(self, api_url: str, username: str, password: str):
        # Do not rstrip('/') here, as the panel path might be the root itself.
        self.api_url = api_url
        self.username = username
        self.password = password

    @abstractmethod
    async def login(self) -> bool:
        """Logs into the panel and returns True on success, False otherwise."""
        pass

# ===== MARZBAN PANEL MANAGER =====
class MarzbanPanel(BasePanelManager):
    """Manager for Marzban panels."""
    async def login(self) -> bool:
        try:
            # Marzban API path is fixed relative to the base URL
            api_url = self.api_url.rstrip('/')
            async with httpx.AsyncClient(verify=False) as client:
                login_url = f"{api_url}/api/admin/token"
                data = {"username": self.username, "password": self.password}
                response = await client.post(login_url, data=data)

                if response.status_code == 200 and "access_token" in response.json():
                    return True
                print(f"[Marzban Login Failed] Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print(f"[Marzban Login Error] {e}")
            return False

# ===== SANAEI (X-UI) PANEL MANAGER =====
class SanaeiPanel(BasePanelManager):
    """
    Manager for Sanaei (X-UI) panels.
    It now correctly handles panels with a secret path.
    The user must provide the full base URL including the secret path.
    Example: https://panel.example.com:2053/YourSecretPath
    """
    async def login(self) -> bool:
        try:
            # Ensure the base URL does not end with a slash, then add /login
            base_url = self.api_url.rstrip('/')
            login_url = f"{base_url}/login"
            
            async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                print(f"[Sanaei Login Attempt] URL: {login_url}") # Debugging line
                data = {"username": self.username, "password": self.password}
                response = await client.post(login_url, data=data)
                
                # Check for successful login cookie
                if response.status_code == 200 and "session" in response.cookies:
                    print(f"[Sanaei Login Success] Status: {response.status_code}")
                    return True

                print(f"[Sanaei Login Failed] Status: {response.status_code}, Response: {response.text}")
                return False
        except httpx.ConnectError as e:
            print(f"[Sanaei Connection Error] Could not connect to {self.api_url}. Error: {e}")
            return False
        except Exception as e:
            print(f"[Sanaei Login Error] An unexpected error occurred: {e}")
            return False

# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    """Factory function to get the correct panel manager instance."""
    panel_classes = {
        "marzban": MarzbanPanel,
        "sanaei": SanaeiPanel,
    }
    manager_class = panel_classes.get(panel_type)
    if manager_class:
        return manager_class(api_url, username, password)
    return None
