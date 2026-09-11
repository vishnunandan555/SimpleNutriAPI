from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base

class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=True)
    organization: Mapped[str] = mapped_column(String(255), nullable=True)
    country: Mapped[str] = mapped_column(String(10), nullable=True)
    url: Mapped[str] = mapped_column(String(512), nullable=True)
    basis: Mapped[str] = mapped_column(String(128), nullable=True)
    license_status: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
