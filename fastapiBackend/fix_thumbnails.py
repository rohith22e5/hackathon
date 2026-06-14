"""
Converts Google Drive view URLs to direct image URLs in products collection.
"""
import asyncio, re
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class Product(Document):
    name: str
    thumbnail: Optional[str] = None
    points_price: int = Field(..., ge=0)
    product_type: str = "ebook"
    stock: Optional[int] = None
    is_digital: bool = True
    is_active: bool = True
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"


def to_direct_url(url: str) -> str:
    match = re.search(r"/file/d/([^/]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return url


async def fix():
    from motor.motor_asyncio import AsyncIOMotorClient as _C
    if not hasattr(_C, "append_metadata"):
        _C.append_metadata = lambda *a, **kw: None

    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME", "smartedu_db")]
    await init_beanie(database=db, document_models=[Product])

    products = await Product.find_all().to_list()
    updated = 0
    for p in products:
        if p.thumbnail and "/file/d/" in p.thumbnail:
            new_url = to_direct_url(p.thumbnail)
            print(f"  {p.name}:\n    {p.thumbnail}\n    -> {new_url}")
            p.thumbnail = new_url
            p.updated_at = datetime.utcnow()
            await p.save()
            updated += 1

    print(f"\nDone. {updated} products updated.")
    client.close()


if __name__ == "__main__":
    asyncio.run(fix())
