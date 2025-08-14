# ===== IMPORTS & DEPENDENCIES =====
import httpx
import json
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

# ===== BASE PANEL MANAGER (Interface) =====
class BasePanelManager(ABC):
    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.session: Optional[httpx.AsyncClient] = None

    @abstractmethod
    async def login(self) -> bool:
        pass

    @abstractmethod
    async def get_inbounds(self) -> List[Dict[str, Any]]:
        pass
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(verify=False, timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.is_closed:
            await self.session.aclose()


# ===== MARZBAN PANEL MANAGER =====
class MarzbanPanel(BasePanelManager):
    async def login(self) -> bool:
        if not self.session: return False
        try:
            api_url = self.api_url.rstrip('/')
            login_url = f"{api_url}/api/admin/token"
            data = {"username": self.username, "password": self.password}
            response = await self.session.post(login_url, data=data)
            if response.status_code == 200 and "access_token" in response.json():
                self.session.headers.update({"Authorization": f"Bearer {response.json()['access_token']}"})
                return True
            return False
        except Exception: return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not await self.login(): return []
        print("Marzban get_inbounds is currently a placeholder.")
        return [{"id": 1, "remark": "پلن پیش‌فرض مرزبان"}] 


# ===== SANAEI (X-UI) PANEL MANAGER =====
class SanaeiPanel(BasePanelManager):
    async def login(self) -> bool:
        if not self.session:
            print("[SanaeiPanel] Login failed: session is not initialized.")
            return False
        
        print("[SanaeiPanel] Attempting to login...")
        try:
            base_url = self.api_url.rstrip('/')
            login_url = f"{base_url}/login"
            data = {"username": self.username, "password": self.password}
            response = await self.session.post(login_url, data=data)
            
            is_successful_body = False
            try:
                if response.json().get("success") is True: is_successful_body = True
            except Exception: pass

            has_cookie = "session" in self.session.cookies or "x-ui" in self.session.cookies
            
            if response.status_code == 200 and (is_successful_body or has_cookie):
                print("[SanaeiPanel] Login SUCCESSFUL. Cookies are now stored in session.")
                return True
            
            print(f"[SanaeiPanel] Login FAILED. Status: {response.status_code}, Response: {response.text}")
            return False
        except Exception as e:
            print(f"[SanaeiPanel] Login EXCEPTION: {e}")
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        # The context manager in user_handlers.py ensures session is created.
        # This method assumes we are already in a context.
        if not self.session:
             print("[SanaeiPanel] get_inbounds failed because session is not initialized.")
             return []

        if not await self.login():
            print("[SanaeiPanel] get_inbounds failed because login was unsuccessful.")
            return []
        
        try:
            base_url = self.api_url.rstrip('/')
            inbounds_url = f"{base_url}/panel/api/inbounds/list"
            print(f"[SanaeiPanel] Fetching inbounds from URL: {inbounds_url}")
            
            # The session now holds the login cookies, so this request should be authenticated.
            response = await self.session.get(inbounds_url)
            
            print(f"[SanaeiPanel] Get inbounds response status: {response.status_code}")
            print(f"[SanaeiPanel] Get inbounds raw response text: {response.text}") # Print raw text for debugging
            
            # Now, try to parse JSON
            response_data = response.json()
            if response_data.get("success"):
                inbounds_list = response_data.get("obj", [])
                print(f"[SanaeiPanel] Successfully parsed {len(inbounds_list)} inbounds.")
                return inbounds_list
            else:
                print("[SanaeiPanel] Get inbounds request was not successful according to JSON body.")
                return []
        except json.JSONDecodeError as e:
            print(f"[SanaeiPanel] JSONDecodeError: Failed to parse response as JSON. Error: {e}")
            return []
        except Exception as e:
            print(f"[SanaeiPanel] Get inbounds EXCEPTION: {e}")
            return []

# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
