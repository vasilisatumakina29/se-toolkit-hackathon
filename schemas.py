from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ItemStatus, ItemType


class ItemBase(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=5, max_length=1000)
    category: str = Field(min_length=2, max_length=50)
    location: str = Field(min_length=2, max_length=120)
    contact: str = Field(min_length=2, max_length=120)
    item_type: ItemType


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    status: ItemStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
