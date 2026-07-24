from __future__ import annotations

from pathlib import Path

from app.config import AppConfig, ROOT_DIR


class RagService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._vector_store = None

    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = self._create_vector_store()
        return self._vector_store

    def _create_vector_store(self):
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_qdrant import QdrantVectorStore
        from qdrant_client import QdrantClient

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        if self.config.qdrant_mode == "local":
            client = QdrantClient(path=str(ROOT_DIR / "data" / "qdrant"))
        else:
            client = QdrantClient(url=self.config.qdrant_url, api_key=self.config.qdrant_api_key or None)

        return QdrantVectorStore(
            client=client,
            collection_name=self.config.qdrant_collection,
            embedding=embeddings,
        )

    def ensure_index(self) -> int:
        """Create a missing collection only; existing knowledge is never deleted."""
        from langchain_core.documents import Document
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_qdrant import QdrantVectorStore
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from qdrant_client import QdrantClient

        if self.config.qdrant_mode == "local":
            client = QdrantClient(path=str(ROOT_DIR / "data" / "qdrant"))
        else:
            client = QdrantClient(url=self.config.qdrant_url, api_key=self.config.qdrant_api_key or None)
        if client.collection_exists(self.config.qdrant_collection):
            return 0

        source_dir = ROOT_DIR / "knowledge_base"
        documents = [
            Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": str(path.name)})
            for path in source_dir.glob("*.md")
        ]
        if not documents:
            raise RuntimeError("No Markdown files were found in knowledge_base/.")

        chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)
        QdrantVectorStore.from_documents(
            chunks,
            HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
            client=client,
            collection_name=self.config.qdrant_collection,
        )
        self._vector_store = None
        return len(chunks)
