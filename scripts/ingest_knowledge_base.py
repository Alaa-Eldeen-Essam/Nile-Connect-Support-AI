from app.config import AppConfig
from app.services.rag_service import RagService

if __name__ == "__main__":
    count = RagService(AppConfig.from_env()).ensure_index()
    print(f"Knowledge-base ingestion complete: {count} chunks added.")
