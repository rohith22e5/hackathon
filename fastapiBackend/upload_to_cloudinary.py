"""
Downloads product images from Google Drive, uploads to Cloudinary (unsigned),
then updates MongoDB product thumbnails with the Cloudinary URLs.

Usage: python upload_to_cloudinary.py
"""
import asyncio
import re
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from pydantic import Field
from typing import Optional


CLOUDINARY_CLOUD_NAME = "djpofutmw"
CLOUDINARY_UPLOAD_PRESET = "foursome"
CLOUDINARY_UPLOAD_URL = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload"


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


def extract_drive_id(url: str) -> Optional[str]:
    match = re.search(r"/file/d/([^/]+)|[?&]id=([^&]+)", url)
    if match:
        return match.group(1) or match.group(2)
    return None


def download_from_drive(file_id: str) -> Optional[bytes]:
    """Download file bytes from Google Drive, handling the virus-scan redirect."""
    session = requests.Session()
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resp = session.get(url, stream=True, timeout=30)

    # Handle Google's large-file confirmation page
    if "Content-Disposition" not in resp.headers:
        # Look for confirmation token in response
        token_match = re.search(r'confirm=([0-9A-Za-z_\-]+)', resp.text)
        if token_match:
            token = token_match.group(1)
            resp = session.get(
                f"https://drive.google.com/uc?export=download&confirm={token}&id={file_id}",
                stream=True, timeout=30
            )
        else:
            # Try the newer export format
            resp = session.get(
                f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0&confirm=t",
                stream=True, timeout=30
            )

    content = b"".join(resp.iter_content(chunk_size=8192))
    if len(content) < 1000:
        print(f"    WARNING: Downloaded only {len(content)} bytes — may be error page")
        return None
    return content


def upload_to_cloudinary(image_bytes: bytes, public_id: str) -> Optional[str]:
    """Upload bytes to Cloudinary using unsigned preset. Returns secure_url."""
    resp = requests.post(
        CLOUDINARY_UPLOAD_URL,
        data={
            "upload_preset": CLOUDINARY_UPLOAD_PRESET,
            "public_id": f"marketplace/{public_id}",
        },
        files={"file": ("image.jpg", image_bytes, "image/jpeg")},
        timeout=60,
    )
    if resp.status_code == 200:
        return resp.json().get("secure_url")
    print(f"    Cloudinary error {resp.status_code}: {resp.text[:200]}")
    return None


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


async def run():
    from motor.motor_asyncio import AsyncIOMotorClient as _C
    if not hasattr(_C, "append_metadata"):
        _C.append_metadata = lambda *a, **kw: None

    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME", "smartedu_db")]
    await init_beanie(database=db, document_models=[Product])

    products = await Product.find_all().to_list()
    updated = 0

    for p in products:
        if not p.thumbnail:
            print(f"  SKIP (no thumbnail): {p.name}")
            continue

        # Already on Cloudinary
        if "cloudinary.com" in p.thumbnail:
            print(f"  SKIP (already Cloudinary): {p.name}")
            continue

        file_id = extract_drive_id(p.thumbnail)
        if not file_id:
            print(f"  SKIP (can't extract Drive ID): {p.name} — {p.thumbnail}")
            continue

        print(f"  Processing: {p.name}")
        print(f"    Drive ID: {file_id}")

        image_bytes = download_from_drive(file_id)
        if not image_bytes:
            print(f"    FAILED to download")
            continue
        print(f"    Downloaded {len(image_bytes):,} bytes")

        cloudinary_url = upload_to_cloudinary(image_bytes, slugify(p.name))
        if not cloudinary_url:
            print(f"    FAILED to upload")
            continue
        print(f"    Cloudinary URL: {cloudinary_url}")

        p.thumbnail = cloudinary_url
        p.updated_at = datetime.utcnow()
        await p.save()
        updated += 1
        print(f"    DB updated OK")

    print(f"\nDone. {updated}/{len(products)} products updated.")
    client.close()


if __name__ == "__main__":
    asyncio.run(run())
