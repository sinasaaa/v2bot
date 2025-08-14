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
        # Simulate a browser User-Agent, as some panels might require it.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = httpx.AsyncClient(verify=False, timeout=15.0, headers=headers)
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
        # This is a placeholder and needs to be implemented based on Marzban's logic
        return [{"id": 1, "remark": "پلن پیش‌فرض مرزبان"}] 


# ===== SANAEI (X-UI) PANEL MANAGER (Final Version based on Mirza Bot Code) =====
class SanaeiPanel(BasePanelManager):
    async def login(self) -> bool:
        if not self.session: return False
        try:
            base_url = self.api_url.rstrip('/')
            login_url = f"{base_url}/login"
            # Mirza bot sends data as 'application/x-www-form-urlencoded'
            data = {"username": self.username, "password": self.password}
            
            print(f"[Sanaei Final] Attempting login to: {login_url}")
            response = await self.session.post(login_url, data=data)
            
            print(f"[Sanaei Final] Login response status: {response.status_code}")
            print(f"[Sanaei Final] Login response cookies: {self.session.cookies.keys()}")

            if response.status_code == 200 and ("session" in self.session.cookies or "x-ui" in self.session.cookies):
                print("[Sanaei Final] Login SUCCESSFUL.")
                return True

            print(f"[Sanaei Final] Login FAILED. Response text: {response.text[:200]}") # Show first 200 chars
            return False
        except Exception as e:
            print(f"[Sanaei Final] Login EXCEPTION: {e}")
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not self.session or not await self.login():
            return []
        
        try:
            base_url = self.api_url.rstrip('/')
            inbounds_url = f"{base_url}/panel/api/inbounds/list"
            print(f"[Sanaei Final] Fetching inbounds from: {inbounds_url}")
            
            response = await self.session.get(inbounds_url)
            
            print(f"[Sanaei Final] Get inbounds response status: {response.status_code}")
            if not response.text:
                print("[Sanaei Final] Get inbounds response body is EMPTY.")
                return []
                
            response_data = response.json()
            if not response_data.get("success"):
                print(f"[Sanaei Final] API reports failure: {response_data.get('msg')}")
                return []
                
            raw_inbounds = response_data.get("obj", [])
            plans = []
            for inbound in raw_inbounds:
                remark = inbound.get("remark")
                inbound_id = inbound.get("id")
                if remark and inbound_id is not None:
                    plans.append({"id": inbound_id, "remark": remark})

            print(f"Successfully extracted {len(plans)} plans.")
            return plans
            
        except json.JSONDecodeError:
            print(f"[Sanaei Final] JSONDecodeError. Raw response was: {response.text[:500]}") # Show first 500 chars
            return []
        except Exception as e:
            print(f"[Sanaei Final] An exception occurred in get_inbounds: {e}")
            return []


# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
