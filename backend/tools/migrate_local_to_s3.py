"""Simple migration tool to copy local stored files to S3 and update DB paths.

Usage: run in container or environment with app settings configured.
"""
import os
import argparse
from app.core.config import settings
from app.storage import LocalStorage, S3Storage, get_storage_driver
from app.db.database import SessionLocal
from app.models.asset import Asset


def migrate(dry_run: bool = True, limit: int | None = None):
    # Only supports migrating from local to s3
    if settings.STORAGE_DRIVER == "s3":
        print("Warning: STORAGE_DRIVER currently set to s3; this tool expects local source. Continue?")

    local = LocalStorage(settings.LOCAL_STORAGE_PATH)
    s3 = S3Storage()

    db = SessionLocal()
    try:
        query = db.query(Asset).filter(Asset.path != None)
        total = query.count()
        print(f"Found {total} assets to consider")
        if limit:
            query = query.limit(limit)
        for asset in query:
            src = asset.path
            print(f"Migrating {asset.id} -> {src}")
            # read local
            data = local.get(src)
            from io import BytesIO
            key = s3.put(BytesIO(data), os.path.basename(src), asset.purpose, asset.owner_id, asset.is_public)
            print(f"Uploaded to {key}")
            if not dry_run:
                asset.path = key
                db.add(asset)
                db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    migrate(dry_run=args.dry_run, limit=args.limit)
