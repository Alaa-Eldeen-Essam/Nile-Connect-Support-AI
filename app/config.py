from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AppConfig:
    app_env: str
    app_name: str
    google_api_key: str
    mongo_uri: str
    mongo_db: str
    profile_storage: str
    sqlite_path: Path
    qdrant_mode: str
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str
    settings_encryption_key: str
    settings_admin_token: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            app_name=os.getenv("APP_NAME", "WE Telecom AI Agent"),
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            mongo_uri=os.getenv("MONGO_URI", "mongodb://mongo:27017"),
            mongo_db=os.getenv("MONGO_DB", "we_telecom_db"),
            profile_storage=os.getenv("PROFILE_STORAGE", "sqlite"),
            sqlite_path=ROOT_DIR / os.getenv("SQLITE_PATH", "data/we_telecom.db"),
            qdrant_mode=os.getenv("QDRANT_MODE", "container"),
            qdrant_url=os.getenv("QDRANT_URL", "http://qdrant:6333"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
            qdrant_collection=os.getenv("QDRANT_COLLECTION", "we_knowledge_base"),
            settings_encryption_key=os.getenv("SETTINGS_ENCRYPTION_KEY", ""),
            settings_admin_token=os.getenv("SETTINGS_ADMIN_TOKEN", ""),
        )

    def with_runtime_values(self, values: dict[str, str]) -> "AppConfig":
        allowed = {
            "GOOGLE_API_KEY": "google_api_key",
            "MONGO_URI": "mongo_uri",
            "QDRANT_URL": "qdrant_url",
            "QDRANT_API_KEY": "qdrant_api_key",
        }
        return replace(self, **{allowed[key]: value for key, value in values.items() if key in allowed})

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
