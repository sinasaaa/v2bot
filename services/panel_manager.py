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
        """
        In x-ui, 'inbounds' are connection protocols, and inside each inbound,
        there are 'clients' which we will treat as sales plans.
        This function will extract the first client from each inbound as a plan.
        """
        if not self.session or not await self.login():
            return []
        
        try:
            base_url = self.api_url.rstrip('/')
            inbounds_url = f"{base_url}/panel/api/inbounds/list"
            response = await self.session.get(inbounds_url)
            
            if response.status_code != 200:
                return []

            response_data = response.json()
            if not response_data.get("success"):
                return []
                
            raw_inbounds = response_data.get("obj", [])
            
            # This will be our list of "plans"
            plans = []
            
            for inbound in raw_inbounds:
                try:
                    # settings is a JSON string, so we need to parse it
                    settings_str = inbound.get("settings", "{}")
                    settings_obj = json.loads(settings_str)
                    
                    clients = settings_obj.get("clients", [])
                    
                    if clients:
                        # We will treat the FIRST client of each inbound as a "plan template"
                        first_client_as_plan = clients[0]
                        
                        # The "remark" of the inbound is the plan name
                        plan_name = inbound.get("remark", f"پلن ناشناس {inbound.get('id')}")
                        
                        # The ID of the plan is the inbound's ID
                        plan_id = inbound.get("id")
                        
                        plans.append({"id": plan_id, "remark": plan_name})

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Could not parse settings for inbound {inbound.get('id')}: {e}")
                    continue

            print(f"Successfully extracted {len(plans)} plans from inbounds.")
            return plans
            
        except Exception as e:
            print(f"An exception occurred in get_inbounds: {e}")
            return []


# ===== FACTORY FUNCTION =====
def get_panel_manager(panel_type: str, api_url: str, username: str, password: str) -> Optional[BasePanelManager]:
    panel_classes = { "marzban": MarzbanPanel, "sanaei": SanaeiPanel }
    manager_class = panel_classes.get(panel_type)
    return manager_class(api_url, username, password) if manager_class else None
