from app.core.config import settings
from .base import StorageDriver
from .local import LocalStorage
from .s3 import S3Storage


def get_storage_driver() -> StorageDriver:
    driver = (settings.STORAGE_DRIVER or "local").lower()
    if driver == "s3":
        return S3Storage()
    return LocalStorage()
