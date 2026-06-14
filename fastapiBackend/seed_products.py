"""
Run once to seed marketplace products into MongoDB.
Usage: python seed_products.py
"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from pydantic import Field, HttpUrl
from typing import Optional
from datetime import datetime


class Product(Document):
    category: Optional[object] = None
    name: str
    description: Optional[str] = ""
    product_type: str = "ebook"
    points_price: int = Field(..., ge=0)
    stock: Optional[int] = None
    is_digital: bool = True
    digital_file_path: Optional[str] = None
    external_url: Optional[str] = None
    thumbnail: Optional[str] = None
    metadata: Optional[dict] = None
    is_active: bool = True
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"


PRODUCTS = [
    {
        "name": "Gurukul Signature Cap",
        "description": "Adjustable premium cotton cap with embroidered Gurukul logo. Perfect for campus events.",
        "product_type": "physical",
        "points_price": 25,
        "stock": 50,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1Qi6AO4ocF2XXIbGy4kokEiTKwmB54ycp/view?usp=drive_link",
        "is_active": True,
        "featured": True,
    },
    {
        "name": "Gurukul Precision Pen",
        "description": "Sleek metal ballpoint pen with black ink and an engraved Gurukul crest.",
        "product_type": "physical",
        "points_price": 10,
        "stock": 200,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1JO-lQ7OandtqmGedImeKUL15UhjEDdIv/view?usp=drive_link",
        "is_active": True,
        "featured": False,
    },
    {
        "name": "Scholar's Tactical Backpack",
        "description": "Durable, water-resistant backpack with a dedicated laptop compartment and Gurukul branding.",
        "product_type": "physical",
        "points_price": 85,
        "stock": 15,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1XN7X1cVTVQiWAHOFlko7PZoVQDCB2N25/view?usp=drive_link",
        "is_active": True,
        "featured": True,
    },
    {
        "name": "STEM Legends Sticker Pack",
        "description": "Set of 12 high-quality vinyl stickers featuring famous scientists and mathematical constants.",
        "product_type": "physical",
        "points_price": 5,
        "stock": 150,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1k_i_KNAgp5OytlXtcEBzTSkeT0w5RreV/view?usp=drive_link",
        "is_active": True,
        "featured": False,
    },
    {
        "name": "Gurukul Academic Notebook",
        "description": "200-page hardcover notebook with dotted grid paper, ideal for physics and math equations.",
        "product_type": "physical",
        "points_price": 15,
        "stock": 100,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1-FkuoUuJHEaXycRFP1KqcI_sIvv8n2EA/view?usp=drive_link",
        "is_active": True,
        "featured": True,
    },
    {
        "name": "Academic Excellence Lapel Pin",
        "description": "Gold-plated enamel badge for top-performing students to display on their jackets.",
        "product_type": "physical",
        "points_price": 30,
        "stock": 40,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1doX5bFmjUnIWRCz6jy0VQP3Av9l8y2sE/view?usp=drive_link",
        "is_active": True,
        "featured": False,
    },
    {
        "name": "Gurukul Insulated Water Bottle",
        "description": "Matte black stainless steel water bottle, keeps drinks cold for 24 hours. Features laser-etched logo.",
        "product_type": "physical",
        "points_price": 45,
        "stock": 30,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1D420YVIET1ALp7KTGPkrMbRt1JkeA-mi/view?usp=drive_link",
        "is_active": True,
        "featured": True,
    },
    {
        "name": "Science Kit",
        "description": "A science kit consisting of various tools to perform experiments featuring the Gurukul Science Department insignia and an ID clip.",
        "product_type": "physical",
        "points_price": 8,
        "stock": 120,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1DFFw0CJ4-3J7zylPLU4O38mIRaRVoQxV/view?usp=drive_link",
        "is_active": True,
        "featured": False,
    },
    {
        "name": "Campus Hoodie",
        "description": "Heavyweight fleece hoodie in dark navy with the Gurukul crest printed on the chest.",
        "product_type": "physical",
        "points_price": 100,
        "stock": 25,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1cwaA4thQC2Y-w6HtwmgqLHKS4YiWjxea/view?usp=drive_link",
        "is_active": True,
        "featured": True,
    },
    {
        "name": "Lab Safety Goggles",
        "description": "Standard issue scratch-resistant safety goggles with the Gurukul lab certification stamp.",
        "product_type": "physical",
        "points_price": 20,
        "stock": 60,
        "is_digital": False,
        "thumbnail": "https://drive.google.com/file/d/1BB_0RfLIzbCHD55hBiaMh6zyskpc1WYp/view?usp=drive_link",
        "is_active": True,
        "featured": False,
    },
]


async def seed():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "smartedu_db")

    if not hasattr(__import__("motor.motor_asyncio", fromlist=["AsyncIOMotorClient"]).AsyncIOMotorClient, "append_metadata"):
        from motor.motor_asyncio import AsyncIOMotorClient as _C
        _C.append_metadata = lambda *a, **kw: None

    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    await init_beanie(database=db, document_models=[Product])

    inserted = 0
    skipped = 0
    for p in PRODUCTS:
        exists = await Product.find_one(Product.name == p["name"])
        if exists:
            print(f"  SKIP (exists): {p['name']}")
            skipped += 1
            continue
        doc = Product(**p)
        await doc.insert()
        print(f"  INSERTED: {p['name']}")
        inserted += 1

    print(f"\nDone. {inserted} inserted, {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
