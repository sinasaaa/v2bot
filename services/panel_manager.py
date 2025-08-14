# ===== IMPORTS & DEPENDENCIES =====
import httpx
from abc import ABC, abstractmethod
from typing import Optional
# ===== BASE PANEL MANAGER (Interface) =====
class BasePanelManager(ABC):
    """Abstract base class for all panel managers."""
    def __init__(self, api_url: str, username: str, password: str):
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
    It now correctly handles panels with a secret path and different cookie names.
    """
    async def login(self) -> bool:
        try:
            base_url = self.api_url.rstrip('/')
            login_url = f"{base_url}/login"
            
            async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                print(f"[Sanaei Login Attempt] URL: {login_url}")
                data = {"username": self.username, "password": self.password}
                response = await client.post(login_url, data=data)
                
                # --- THE FIX IS HERE ---
                # Check for successful login based on response body OR cookie.
                # This makes it compatible with more x-ui versions.
                
                is_successful_body = False
                try:
                    json_response = response.json()
                    if json_response.get("success") is True:
                        is_successful_body = True
                except Exception:
                    # Response was not JSON, which is fine.
                    pass

                has_session_cookie = "session" in response.cookies
                has_xui_cookie = "x-ui" in response.cookies

                if response.status_code == 200 and (is_successful_body or has_session_cookie or has_xui_cookie):
                    print(f"[Sanaei Login Success] Status: {response.status_code}. Method: Body/Cookie.")
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
