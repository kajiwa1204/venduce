from __future__ import annotations
import os
from typing import BinaryIO
from datetime import datetime, timezone
import uuid
import hmac
import hashlib
from urllib.parse import urlencode

from app.core.config import settings
from .base import StorageDriver


class LocalStorage(StorageDriver):
    def __init__(self, base_path: str | None = None):
        self.base_path = base_path or settings.LOCAL_STORAGE_PATH
        os.makedirs(self.base_path, exist_ok=True)

    def _ensure_dir(self, path: str) -> None:
        os.makedirs(os.path.join(self.base_path, path), exist_ok=True)

    def _generate_name(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        uid = uuid.uuid4().hex
        return f"{uid}{ext}"

    def put(self, file: BinaryIO, filename: str, purpose: str, owner_id: int | None, public: bool) -> str:
        date = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        rel_dir = os.path.join(purpose, date)
        self._ensure_dir(rel_dir)
        name = self._generate_name(filename)
        rel_path = os.path.join(rel_dir, name).replace('\\', '/')
        abs_path = os.path.join(self.base_path, rel_path)
        # write
        with open(abs_path, "wb") as f:
            f.write(file.read())
        # safe permissions
        try:
            os.chmod(abs_path, 0o644)
        except Exception:
            pass
        return rel_path

    def get(self, path: str) -> bytes:
        abs_path = os.path.join(self.base_path, path)
        with open(abs_path, "rb") as f:
            return f.read()

    def delete(self, path: str) -> None:
        abs_path = os.path.join(self.base_path, path)
        try:
            os.remove(abs_path)
        except FileNotFoundError:
            return

    def generate_signed_url(self, path: str, ttl_seconds: int = 3600) -> str:
        # Generate a signed URL that points to the app's asset serve endpoint
        expires = int(datetime.now(timezone.utc).timestamp()) + ttl_seconds
        secret = (settings.JWT_SECRET_KEY or "").encode()
        payload = f"{path}:{expires}".encode()
        sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        qs = urlencode({"path": path, "expires": expires, "sig": sig})
        return f"/api/assets/serve?{qs}"
