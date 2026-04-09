from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ItemType(str, Enum):
    LOST = "lost"
    FOUND = "found"


class ItemStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"


def utcnow_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    contact: Mapped[str] = mapped_column(String(120), nullable=False)
    item_type: Mapped[ItemType] = mapped_column(SqlEnum(ItemType), nullable=False)
    status: Mapped[ItemStatus] = mapped_column(SqlEnum(ItemStatus), default=ItemStatus.OPEN, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    image_mime_type: Mapped[str] = mapped_column(String(50), nullable=True)
    image_filename: Mapped[str] = mapped_column(String(255), nullable=True)
