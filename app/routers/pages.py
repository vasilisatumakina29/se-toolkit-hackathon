from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item, ItemStatus, ItemType
from app.schemas import ItemCreate

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")

MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_PHOTO_TYPES = {
    "image/jpeg",
    "image/png",
}

CATEGORIES = [
    "Electronics",
    "Documents",
    "Keys",
    "Clothes",
    "Accessories",
    "Other",
]


def _extract_photo_payload(photo: UploadFile | None) -> dict[str, bytes | str]:
    if photo is None or not photo.filename:
        return {}

    if photo.content_type not in ALLOWED_PHOTO_TYPES:
        raise ValueError("Please upload a JPG or PNG image.")

    image_data = photo.file.read(MAX_PHOTO_SIZE_BYTES + 1)
    if not image_data:
        raise ValueError("Uploaded photo is empty.")
    if len(image_data) > MAX_PHOTO_SIZE_BYTES:
        raise ValueError("Photo must be 5 MB or smaller.")

    return {
        "image_data": image_data,
        "image_mime_type": photo.content_type,
        "image_filename": Path(photo.filename).name,
    }

@router.get("/")
def home(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    item_type: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
):
    normalized_item_type = item_type if item_type in {member.value for member in ItemType} else None
    normalized_status = (
        status_filter
        if status_filter in {member.value for member in ItemStatus}
        else ItemStatus.OPEN.value
    )

    query = select(Item).order_by(Item.created_at.desc())
    if normalized_item_type:
        query = query.where(Item.item_type == ItemType(normalized_item_type))
    query = query.where(Item.status == ItemStatus(normalized_status))
    if search:
        like_pattern = f"%{search.strip()}%"
        query = query.where(Item.title.ilike(like_pattern) | Item.description.ilike(like_pattern))

    items = list(db.scalars(query))
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "items": items,
            "item_type": normalized_item_type or "",
            "status_filter": normalized_status,
            "search": search or "",
        },
    )


@router.get("/items/new")
def new_item_form(request: Request):
    return templates.TemplateResponse(
        request,
        "create_item.html",
        {"categories": CATEGORIES, "errors": {}, "form_data": {}},
    )


@router.post("/items")
def create_item(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    category: Annotated[str, Form()],
    location: Annotated[str, Form()],
    contact: Annotated[str, Form()],
    item_type: Annotated[ItemType, Form()],
    photo: Annotated[UploadFile | None, File()] = None,
):
    form_data = {
        "title": title,
        "description": description,
        "category": category,
        "location": location,
        "contact": contact,
        "item_type": item_type.value,
    }

    try:
        payload = ItemCreate(**form_data)
    except Exception as exc:
        errors = {"form": str(exc)}
        return templates.TemplateResponse(
            request,
            "create_item.html",
            {
                "categories": CATEGORIES,
                "errors": errors,
                "form_data": form_data,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        photo_payload = _extract_photo_payload(photo)
    except ValueError as exc:
        errors = {"form": str(exc)}
        return templates.TemplateResponse(
            request,
            "create_item.html",
            {
                "categories": CATEGORIES,
                "errors": errors,
                "form_data": form_data,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    item = Item(**payload.model_dump(), **photo_payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return RedirectResponse(url=f"/items/{item.id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/items/{item_id}")
def item_details(request: Request, item_id: int, db: Annotated[Session, Depends(get_db)]):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(request, "item_detail.html", {"item": item})


@router.get("/items/{item_id}/image")
def item_image(item_id: int, db: Annotated[Session, Depends(get_db)]):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not item.image_data or not item.image_mime_type:
        raise HTTPException(status_code=404, detail="Item image not found")

    headers: dict[str, str] = {}
    if item.image_filename:
        safe_filename = item.image_filename.replace('"', "")
        headers["Content-Disposition"] = f'inline; filename="{safe_filename}"'

    return Response(content=item.image_data, media_type=item.image_mime_type, headers=headers)


@router.post("/items/{item_id}/resolve")
def resolve_item(item_id: int, db: Annotated[Session, Depends(get_db)]):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = ItemStatus.RESOLVED
    db.commit()
    return RedirectResponse(url=f"/items/{item.id}", status_code=status.HTTP_303_SEE_OTHER)
