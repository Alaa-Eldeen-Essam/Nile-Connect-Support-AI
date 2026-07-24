from __future__ import annotations

import sqlite3
from typing import Protocol

from app.models.schemas import UserProfile


class ProfileRepository(Protocol):
    def save(self, profile: UserProfile) -> None: ...

    def exists(self, phone: str) -> bool: ...


class SQLiteProfileRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    age INTEGER NOT NULL,
                    city TEXT NOT NULL
                )
                """
            )

    def save(self, profile: UserProfile) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO users (name, phone, age, city) VALUES (?, ?, ?, ?)
                ON CONFLICT(phone) DO UPDATE SET
                    name = excluded.name, age = excluded.age, city = excluded.city
                """,
                (profile.name, profile.phone, profile.age, profile.city),
            )

    def exists(self, phone: str) -> bool:
        with sqlite3.connect(self.database_path) as connection:
            return connection.execute("SELECT 1 FROM users WHERE phone = ?", (phone,)).fetchone() is not None


class MongoProfileRepository:
    def __init__(self, collection: object) -> None:
        self.collection = collection

    def save(self, profile: UserProfile) -> None:
        self.collection.update_one({"phone": profile.phone}, {"$set": profile.model_dump()}, upsert=True)

    def exists(self, phone: str) -> bool:
        return self.collection.find_one({"phone": phone}, {"_id": 1}) is not None
