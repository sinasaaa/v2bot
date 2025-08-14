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
        # Enable following redirects to handle 301/302 responses from the panel.
        self.session = httpx.AsyncClient(verify=False, timeout=15.0, headers=headers, follow_redirects=True)
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
                return True
            return False
        except Exception:
            return False

    async def get_inbounds(self) -> List[Dict[str, Any]]:
        if not self.session or not await self.login():
            return []
        
        try:
            base_url = self.api_url.rstrip('/')
            # Use the most likely standard API path; `follow_redirects=True` will handle variations.
            inbounds_url = f"{base_url}/panel/api/inbounds/list"
            print(f"Attempting to fetch inbounds (will follow redirects): {inbounds_url}")
            
            response = await self.session.get(inbounds_url)
            
            print(f"[Final] Get inbounds response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[Final] Request failed after redirects. Final URL: {response.url}, Text: {response.text[:200]}")
                return []
            
            if not response.text:
                print("[Final] Response body is EMPTY after redirects.")
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

            print(f"Successfully extracted {len(plans)} plans.")
            return plans
            
        except json.JSONDecodeError:
            print(f"[Final] JSONDecodeError. Raw response was: {response.text[:500]}")
            return []
        except Exception as e:
            print(f"An exception occurred in get_inbounds: {e}")
            return []


# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
