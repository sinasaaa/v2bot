# ===== IMPORTS & DEPENDENCIES =====
from sqlalchemy import Column, Integer, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from .user import Base
import enum

# ===== ENUMS & TYPES =====
class PanelType(str, enum.Enum):
    MARZBAN = "marzban"
    SANAEI = "sanaei"
    # Add other panel types here in the future

# ===== PANEL MODEL =====
class V2RayPanel(Base):
    __tablename__ = "v2ray_panels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    panel_type: Mapped[PanelType] = mapped_column(SAEnum(PanelType), nullable=False)
    api_url: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Credentials should be stored encrypted in a real-world scenario
    # For now, we store them as plain text for simplicity.
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self):
        return f"<V2RayPanel(id={self.id}, name='{self.name}', type='{self.panel_type.value}')>"
