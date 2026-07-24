from dataclasses import replace

from cryptography.fernet import Fernet

from app.config import AppConfig
from app.repositories.runtime_settings import RuntimeSettingsStore


class FakeCollection:
    def __init__(self):
        self.document = None

    def find_one(self, _query):
        return self.document

    def replace_one(self, _query, document, upsert=False):
        assert upsert
        self.document = document


class FakeMongo:
    def __init__(self):
        self.collection = FakeCollection()

    @property
    def database(self):
        return {"app_settings": self.collection}


def test_runtime_settings_are_encrypted_and_reloaded():
    config = replace(
        AppConfig.from_env(),
        settings_encryption_key=Fernet.generate_key().decode(),
        settings_admin_token="test-token",
    )
    store = RuntimeSettingsStore(config, FakeMongo())

    store.save({"GOOGLE_API_KEY": "secret"})

    assert store.load() == {"GOOGLE_API_KEY": "secret"}
    assert b"secret" not in store.mongo.collection.document["payload"]
