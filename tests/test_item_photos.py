from __future__ import annotations

from sqlalchemy import func, select

from app.models import Item

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc```\xf8\x0f\x00\x01\x04\x01\x00"
    b"\x18\xdd\x8d\xb1"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def item_form_data() -> dict[str, str]:
    return {
        "title": "Black AirPods case",
        "description": "Found near the library entrance with a small sticker on it.",
        "category": "Electronics",
        "location": "Library entrance",
        "contact": "@finder",
        "item_type": "found",
    }


def item_count(session_local) -> int:
    with session_local() as session:
        return session.scalar(select(func.count(Item.id))) or 0


def test_create_item_without_photo_still_succeeds(client_and_sessionmaker):
    client, session_local = client_and_sessionmaker

    response = client.post(
        "/items",
        data=item_form_data(),
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/items/1"

    with session_local() as session:
        item = session.get(Item, 1)
        assert item is not None
        assert item.image_data is None
        assert item.image_mime_type is None
        assert item.image_filename is None


def test_create_item_with_valid_photo_shows_image_on_detail_page(client_and_sessionmaker):
    client, session_local = client_and_sessionmaker

    response = client.post(
        "/items",
        data=item_form_data(),
        files={"photo": ("airpods.png", PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    assert 'src="/items/1/image"' in response.text
    assert "Photo" in response.text

    with session_local() as session:
        item = session.get(Item, 1)
        assert item is not None
        assert item.image_data == PNG_BYTES
        assert item.image_mime_type == "image/png"
        assert item.image_filename == "airpods.png"


def test_create_item_rejects_unsupported_photo_type(client_and_sessionmaker):
    client, session_local = client_and_sessionmaker

    response = client.post(
        "/items",
        data=item_form_data(),
        files={"photo": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "Please upload a JPG or PNG image." in response.text
    assert item_count(session_local) == 0


def test_create_item_rejects_photo_over_size_limit(client_and_sessionmaker):
    client, session_local = client_and_sessionmaker
    oversized_bytes = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/items",
        data=item_form_data(),
        files={"photo": ("huge.png", oversized_bytes, "image/png")},
    )

    assert response.status_code == 400
    assert "Photo must be 5 MB or smaller." in response.text
    assert item_count(session_local) == 0


def test_image_endpoint_returns_binary_for_item_with_photo(client_and_sessionmaker):
    client, _ = client_and_sessionmaker

    create_response = client.post(
        "/items",
        data=item_form_data(),
        files={"photo": ("airpods.png", PNG_BYTES, "image/png")},
        follow_redirects=False,
    )
    assert create_response.status_code == 303

    response = client.get("/items/1/image")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == PNG_BYTES


def test_image_endpoint_returns_404_for_item_without_photo(client_and_sessionmaker):
    client, _ = client_and_sessionmaker

    create_response = client.post(
        "/items",
        data=item_form_data(),
        follow_redirects=False,
    )
    assert create_response.status_code == 303

    response = client.get("/items/1/image")

    assert response.status_code == 404


def test_json_api_create_read_list_and_resolve_still_work(client_and_sessionmaker):
    client, _ = client_and_sessionmaker
    payload = item_form_data()

    create_response = client.post("/api/items", json=payload)

    assert create_response.status_code == 201
    created_item = create_response.json()
    assert created_item["id"] == 1
    assert created_item["status"] == "open"
    assert "image_data" not in created_item
    assert "image_mime_type" not in created_item
    assert "image_filename" not in created_item

    list_response = client.get("/api/items")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get("/api/items/1")
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == payload["title"]

    resolve_response = client.patch("/api/items/1/resolve")
    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == "resolved"
