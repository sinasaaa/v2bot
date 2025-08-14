# ===== IMPORTS & DEPENDENCIES =====
import httpx
import json
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
        self.session = httpx.AsyncClient(verify=False, timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.is_closed:
            await self.session.aclose()


# ===== MARZBAN PANEL MANAGER =====
class MarzbanPanel(BasePanelManager):
    """Manager for Marzban panels."""
    async def login(self) -> bool:
        # ... (Implementation remains the same)
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
    """Manager for Sanaei (X-UI) panels."""
    async def login(self) -> bool:
        if not self.session: return False
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

            has_cookie = "session" in response.cookies or "x-ui" in response.cookies
            
            if response.status_code == 200 and (is_successful_body or has_cookie):
                print("[SanaeiPanel] Login SUCCESSFUL.")
                return True
            
            print(f"[SanaeiPanel] Login FAILED. Status: {response.status_code}, Response: {response.text}")
            return False
        except Exception as e:
            print(f"[SanaeiPanel] Login EXCEPTION: {e}")
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        print("[SanaeiPanel] Attempting to get inbounds...")
        if not await self.login():
            print("[SanaeiPanel] get_inbounds failed because login failed.")
            return []
        
        if not self.session: return []
        
        try:
            base_url = self.api_url.rstrip('/')
            inbounds_url = f"{base_url}/panel/api/inbounds/list"
            print(f"[SanaeiPanel] Fetching inbounds from URL: {inbounds_url}")
            
            response = await self.session.get(inbounds_url)
            print(f"[SanaeiPanel] Get inbounds response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[SanaeiPanel] Get inbounds raw response: {json.dumps(response_data, indent=2)}")
                
                if response_data.get("success"):
                    inbounds_list = response_data.get("obj", [])
                    print(f"[SanaeiPanel] Found {len(inbounds_list)} inbounds.")
                    return inbounds_list
                else:
                    print("[SanaeiPanel] Get inbounds request was not successful according to JSON body.")
                    return []
            else:
                 print(f"[SanaeiPanel] Get inbounds returned non-200 status. Response: {response.text}")
                 return []
        except Exception as e:
            print(f"[SanaeiPanel] Get inbounds EXCEPTION: {e}")
            return []

# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    # ... (Implementation remains the same)
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
