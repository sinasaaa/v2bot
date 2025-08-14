# ===== IMPORTS & DEPENDENCIES =====
from sqlalchemy.orm import Session
from models.panel import V2RayPanel, PanelType

# ===== CRUD FUNCTIONS FOR PANEL =====
def create_panel(db: Session, name: str, panel_type: PanelType, api_url: str, username: str, password: str) -> V2RayPanel:
    db_panel = V2RayPanel(
        name=name,
        panel_type=panel_type,
        api_url=api_url,
        username=username,
        password=password
    )
    db.add(db_panel)
    db.commit()
    db.refresh(db_panel)
    return db_panel

def get_panels(db: Session):
    return db.query(V2RayPanel).all()

def get_panel_by_name(db: Session, name: str) -> V2RayPanel | None:
    return db.query(V2RayPanel).filter(V2RayPanel.name == name).first()
