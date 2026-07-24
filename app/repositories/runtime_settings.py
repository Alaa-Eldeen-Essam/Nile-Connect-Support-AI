from __future__ import annotations

import json

from cryptography.fernet import Fernet

from app.config import AppConfig
from app.repositories.mongo import MongoGateway


class RuntimeSettingsStore:
    """Stores optional integration overrides encrypted in the existing Mongo database."""

    document_id = "runtime-settings"

    def __init__(self, config: AppConfig, mongo: MongoGateway) -> None:
        self.config = config
        self.mongo = mongo

    @property
    def enabled(self) -> bool:
        return bool(self.config.settings_encryption_key and self.config.settings_admin_token)

    def load(self) -> dict[str, str]:
        if not self.enabled:
            return {}
        document = self.mongo.database["app_settings"].find_one({"_id": self.document_id})
        if not document:
            return {}
        cipher = Fernet(self.config.settings_encryption_key.encode())
        payload = cipher.decrypt(document["payload"])
        return json.loads(payload.decode())

    def save(self, values: dict[str, str]) -> None:
        if not self.enabled:
            raise RuntimeError(
                "Runtime settings require SETTINGS_ENCRYPTION_KEY and SETTINGS_ADMIN_TOKEN."
            )
        cipher = Fernet(self.config.settings_encryption_key.encode())
        payload = cipher.encrypt(json.dumps(values).encode())
        self.mongo.database["app_settings"].replace_one(
            {"_id": self.document_id},
            {"_id": self.document_id, "payload": payload},
            upsert=True,
        )

    @staticmethod
    def masked(values: dict[str, str]) -> dict[str, str]:
        return {key: "Configured" if value else "Not configured" for key, value in values.items()}
