from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item, ItemStatus, ItemType
from app.schemas import ItemCreate, ItemRead

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=list[ItemRead])
def list_items(
    db: Annotated[Session, Depends(get_db)],
    item_type: Annotated[ItemType | None, Query()] = None,
    status_filter: Annotated[ItemStatus | None, Query(alias="status")] = None,
    search: Annotated[str | None, Query()] = None,
) -> list[Item]:
    query = select(Item).order_by(Item.created_at.desc())
    if item_type:
        query = query.where(Item.item_type == item_type)
    if status_filter:
        query = query.where(Item.status == status_filter)
    if search:
        like_pattern = f"%{search.strip()}%"
        query = query.where(Item.title.ilike(like_pattern) | Item.description.ilike(like_pattern))
    return list(db.scalars(query))


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Annotated[Session, Depends(get_db)]) -> Item:
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Annotated[Session, Depends(get_db)]) -> Item:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}/resolve", response_model=ItemRead)
def resolve_item(item_id: int, db: Annotated[Session, Depends(get_db)]) -> Item:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = ItemStatus.RESOLVED
    db.commit()
    db.refresh(item)
    return item
