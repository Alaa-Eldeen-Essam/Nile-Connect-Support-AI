from __future__ import annotations

from app.config import AppConfig
from app.repositories.mongo import MongoGateway
from app.repositories.profiles import MongoProfileRepository, SQLiteProfileRepository
from app.repositories.runtime_settings import RuntimeSettingsStore
from app.services.agent_service import AgentService


class ApplicationServices:
    def __init__(self, config: AppConfig) -> None:
        config.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.mongo = MongoGateway(config)
        self.settings = RuntimeSettingsStore(config, self.mongo)
        self.agent = AgentService(lambda: self.config, self.profile_repository, self.mongo)

    def load_runtime_settings(self) -> None:
        try:
            values = self.settings.load()
        except Exception:
            return
        if values:
            self._apply(values, persist=False)

    def profile_repository(self):
        if self.config.profile_storage == "mongo":
            return MongoProfileRepository(self.mongo.database["profiles"])
        return SQLiteProfileRepository(str(self.config.sqlite_path))

    def update_runtime_settings(self, values: dict[str, str]) -> None:
        merged = self.settings.load()
        merged.update(values)
        self.settings.save(merged)
        self._apply(merged, persist=False)

    def _apply(self, values: dict[str, str], persist: bool) -> None:
        self.config = self.config.with_runtime_values(values)
        self.mongo.reconfigure(self.config)
        self.settings.config = self.config
        self.agent.reload()

    def close(self) -> None:
        self.mongo.close()
