from __future__ import annotations

import certifi

from app.config import AppConfig


class MongoGateway:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._client = None

    def reconfigure(self, config: AppConfig) -> None:
        self.config = config
        if self._client is not None:
            self._client.close()
        self._client = None

    @property
    def database(self):
        if self._client is None:
            from pymongo import MongoClient

            options = {"serverSelectionTimeoutMS": 5000}
            if self.config.mongo_uri.startswith("mongodb+srv://"):
                options["tlsCAFile"] = certifi.where()
            self._client = MongoClient(self.config.mongo_uri, **options)
        return self._client[self.config.mongo_db]

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
