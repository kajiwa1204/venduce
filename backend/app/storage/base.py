from __future__ import annotations
from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageDriver(ABC):
    """抽象ストレージインターフェース

    実装は `put`, `get`, `delete`, `generate_signed_url` を提供すること。
    ``put`` はファイルオブジェクトとメタ情報を受け取り、保存先のパスを返す。
    """

    @abstractmethod
    def put(self, file: BinaryIO, filename: str, purpose: str, owner_id: int | None, public: bool) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get(self, path: str) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, path: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def generate_signed_url(self, path: str, ttl_seconds: int = 3600) -> str:
        raise NotImplementedError()
