from __future__ import annotations

from enum import Enum


class AssetPurpose(str, Enum):
    AVATAR = "avatar"
    POST_IMAGE = "post_image"
    PRODUCT_IMAGE = "product_image"
    CATEGORY_IMAGE = "category_image"
    BRAND_IMAGE = "brand_image"


class ProductStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class あいうえお(str, Enum):
    かきくけこ = "かきくけこ"
    さしすせそ = "さしすせそ"

__all__ = ["AssetPurpose", "ProductStatus"]
