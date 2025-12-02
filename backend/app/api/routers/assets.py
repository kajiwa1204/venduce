from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
import os
import time

from app.db.database import get_db
from app.storage import get_storage_driver
from app.models.asset import Asset
from app.core.config import settings

router = APIRouter(prefix="/api/assets", tags=["assets"])


def _detect_image_mime(data: bytes) -> Optional[str]:
    # naive detection for common formats
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data.startswith(b"RIFF") and b"WEBP" in data[:12]:
        return "image/webp"
    return None


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    purpose: str = Form(...),
    owner_id: Optional[int] = Form(None),
    public: bool = Form(False),
    db: Session = Depends(get_db),
):
    # validation
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="file too large")
    mime = _detect_image_mime(data)
    if not mime or mime not in settings.ALLOWED_IMAGE_MIME_TYPES.split(","):
        raise HTTPException(status_code=400, detail="invalid image type")

    storage = get_storage_driver()
    from io import BytesIO

    path = storage.put(BytesIO(data), file.filename, purpose, owner_id, public)

    asset = Asset(owner_id=owner_id, purpose=purpose, path=path, meta={"mime": mime, "size": len(data)}, is_public=public)
    db.add(asset)
    db.commit()
    db.refresh(asset)

    # url
    url = storage.generate_signed_url(path, ttl_seconds=settings.ASSET_URL_TTL_SECONDS) if not public else storage.generate_signed_url(path, ttl_seconds=settings.ASSET_URL_TTL_SECONDS)

    return {"id": asset.id, "path": asset.path, "url": url}


@router.get("/serve")
def serve(path: str, expires: int, sig: str):
    # verify signature for local storage
    # Only local driver uses this endpoint in our design
    secret = (settings.JWT_SECRET_KEY or "").encode()
    import hmac, hashlib

    expected = hmac.new(secret, f"{path}:{expires}".encode(), hashlib.sha256).hexdigest()
    now = int(time.time())
    if expected != sig or now > int(expires):
        raise HTTPException(status_code=403, detail="invalid or expired signature")

    storage = get_storage_driver()
    data = storage.get(path)
    # simple MIME detection
    mime = _detect_image_mime(data) or "application/octet-stream"
    return Response(content=data, media_type=mime)
