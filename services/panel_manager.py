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
        if not self.session: return False
        try:
            base_url = self.api_url.rstrip('/')
            login_url = f"{base_url}/login"
            data = {"username": self.username, "password": self.password}
            response = await self.session.post(login_url, data=data)
            if response.status_code == 200 and ("session" in self.session.cookies or "x-ui" in self.session.cookies):
                return True
            return False
        except Exception:
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not self.session or not await self.login():
            return []
        
        try:
            base_url = self.api_url.rstrip('/')
            # <<<--- THE FINAL FIX ATTEMPT IS HERE ---<<<
            # Trying a different, more common API endpoint for inbounds
            inbounds_url = f"{base_url}/api/inbounds"
            print(f"Attempting to fetch inbounds from NEW URL: {inbounds_url}")
            
            response = await self.session.get(inbounds_url)
            
            if response.status_code != 200 or not response.text:
                 print(f"Failed to fetch from new URL. Status: {response.status_code}, Body Empty: {not response.text}")
                 return []

            response_data = response.json()
            if not response_data.get("success"):
                 print("Response from new URL was not successful.")
                 return []
            
            # This is our list of "plans"
            plans = []
            raw_inbounds = response_data.get("obj", [])
            for inbound in raw_inbounds:
                plan_name = inbound.get("remark", f"پلن {inbound.get('id')}")
                plan_id = inbound.get("id")
                if plan_name and plan_id is not None:
                    plans.append({"id": plan_id, "remark": plan_name})

            print(f"Successfully extracted {len(plans)} plans from new URL.")
            return plans
            
        except Exception as e:
            print(f"An exception occurred in get_inbounds with new URL: {e}")
            return []


# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
