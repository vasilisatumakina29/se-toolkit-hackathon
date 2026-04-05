from app.database import Base, SessionLocal, engine
from app.models import Item, ItemStatus, ItemType

SAMPLE_ITEMS = [
    {
        "title": "Black AirPods case",
        "description": "Found near the library entrance. Black protective case with minor scratches.",
        "category": "Electronics",
        "location": "Library entrance",
        "contact": "student@innopolis.university",
        "item_type": ItemType.FOUND,
        "status": ItemStatus.OPEN,
    },
    {
        "title": "Blue student ID holder",
        "description": "Lost somewhere between the dormitory and the main building.",
        "category": "Documents",
        "location": "Dormitory / Main building",
        "contact": "@lostlink_demo",
        "item_type": ItemType.LOST,
        "status": ItemStatus.OPEN,
    },
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        has_items = session.query(Item).first()
        if has_items:
            print("Seed skipped: database already contains items.")
            return
        for item_data in SAMPLE_ITEMS:
            session.add(Item(**item_data))
        session.commit()
        print("Seed data created.")


if __name__ == "__main__":
    main()
