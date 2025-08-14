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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
        }
        self.session = httpx.AsyncClient(verify=False, timeout=15.0, headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.is_closed:
            await self.session.aclose()


# ===== MARZBAN PANEL MANAGER =====
class MarzbanPanel(BasePanelManager):
    # ... (Implementation remains the same)
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
        return [{"id": 1, "remark": "پلن پیش‌فرض مرزبان"}] 


# ===== SANAEI / ALIREZA (X-UI) PANEL MANAGER =====
class SanaeiPanel(BasePanelManager):
    async def login(self) -> bool:
        if not self.session: return False
        try:
            base_url = self.api_url.rstrip('/')
            login_url = f"{base_url}/login"
            data = {"username": self.username, "password": self.password}
            
            response = await self.session.post(login_url, data=data)
            
            if response.status_code == 200 and ("session" in self.session.cookies or "x-ui" in self.session.cookies):
                print("[Alireza Panel] Login SUCCESSFUL.")
                return True

            print(f"[Alireza Panel] Login FAILED. Status: {response.status_code}")
            return False
        except Exception as e:
            print(f"[Alireza Panel] Login EXCEPTION: {e}")
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not self.session or not await self.login():
            return []
        
        try:
            base_url = self.api_url.rstrip('/')
            # <<<--- THE FINAL, CORRECT FIX IS HERE ---<<<
            # Using the API path for Alireza's fork of x-ui panel.
            inbounds_url = f"{base_url}/xui/API/inbounds" # Note the different path
            print(f"Attempting to fetch inbounds from Alireza API URL: {inbounds_url}")
            
            response = await self.session.get(inbounds_url)
            
            print(f"[Alireza Panel] Get inbounds response status: {response.status_code}")
            
            if response.status_code != 200 or not response.text:
                 return []

            response_data = response.json()
            if not response_data.get("success"):
                 return []
            
            plans = []
            raw_inbounds = response_data.get("obj", [])
            for inbound in raw_inbounds:
                remark = inbound.get("remark")
                inbound_id = inbound.get("id")
                if remark and inbound_id is not None:
                    plans.append({"id": inbound_id, "remark": remark})

            print(f"Successfully extracted {len(plans)} plans from Alireza panel.")
            return plans
            
        except Exception as e:
            print(f"An exception occurred in Alireza get_inbounds: {e}")
            return []


# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
