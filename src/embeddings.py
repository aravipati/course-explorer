"""
Embeddings and Vector Store module for UBC Course Advisor.

This module handles:
1. Creating embeddings using AWS Bedrock Titan
2. Building and managing the FAISS vector store
3. Retrieval with optional metadata filtering

Design decisions:
- Uses FAISS for vector storage (Python 3.14 compatible, lightweight)
- Implements post-retrieval filtering for metadata queries
- Persists index to disk for fast startup
"""

import json
from pathlib import Path
from typing import Optional

from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config import (
    AWS_REGION,
    DATA_DIR,
    EMBEDDING_MODEL_ID,
    FAISS_INDEX_PATH,
    RETRIEVER_K,
)


def log(msg):
    import sys
    print(f"[EMBED] {msg}", flush=True)
    sys.stdout.flush()


def get_embeddings() -> BedrockEmbeddings:
    """
    Initialize Bedrock embeddings client.

    Returns:
        BedrockEmbeddings configured for Titan Text Embeddings V2
    """
    import boto3
    from botocore.config import Config

    log(f"Initializing Bedrock client for region: {AWS_REGION}")

    # Configure timeout to avoid hanging
    config = Config(
        connect_timeout=5,
        read_timeout=30,
        retries={'max_attempts': 2}
    )

    try:
        log("Creating boto3 client...")
        client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
            config=config,
        )
        log("Bedrock client created successfully")
    except Exception as e:
        log(f"ERROR: Failed to create Bedrock client: {e}")
        raise

    log("Creating BedrockEmbeddings...")
    embeddings = BedrockEmbeddings(
        model_id=EMBEDDING_MODEL_ID,
        region_name=AWS_REGION,
        client=client,
    )
    log("BedrockEmbeddings created successfully")
    return embeddings


def load_courses() -> list[dict]:
    """
    Load course data from JSON file.

    Returns:
        List of course dictionaries
    """
    courses_file = DATA_DIR / "courses.json"
    with open(courses_file, "r") as f:
        data = json.load(f)
    return data["courses"]


def create_documents(courses: list[dict]) -> list[Document]:
    """
    Convert course data to LangChain Documents.

    Each document contains:
    - page_content: Rich text combining course info for semantic search
    - metadata: Structured fields for filtering

    Args:
        courses: List of course dictionaries

    Returns:
        List of LangChain Document objects
    """
    documents = []

    for course in courses:
        # Create rich text content for embedding
        # This is what gets vectorized and searched semantically
        content = f"""Course: {course['course_code']} - {course['title']}

Description: {course['description']}

Prerequisites: {course['prerequisites']}

Department: {course['department']}
Level: {course['level']}
Credits: {course['credits']}"""

        # Metadata preserved for filtering and display
        metadata = {
            "course_code": course["course_code"],
            "title": course["title"],
            "department": course["department"],
            "level": course["level"],
            "credits": course["credits"],
            "prerequisites": course["prerequisites"],
            "source": course.get("source", "UBC Academic Calendar"),
        }

        documents.append(Document(page_content=content, metadata=metadata))

    return documents


def build_vector_store(documents: list[Document], embeddings: BedrockEmbeddings) -> FAISS:
    """
    Build FAISS vector store from documents.

    Args:
        documents: List of LangChain Documents
        embeddings: Bedrock embeddings client

    Returns:
        FAISS vector store
    """
    print(f"Building vector store with {len(documents)} documents...")
    vector_store = FAISS.from_documents(documents, embeddings)
    print("Vector store built successfully!")
    return vector_store


def save_vector_store(vector_store: FAISS, path: Path = FAISS_INDEX_PATH) -> None:
    """
    Persist FAISS index to disk.

    Args:
        vector_store: FAISS vector store to save
        path: Directory to save index files
    """
    path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(path))
    print(f"Vector store saved to {path}")


def load_vector_store(embeddings: BedrockEmbeddings, path: Path = FAISS_INDEX_PATH) -> FAISS:
    """
    Load FAISS index from disk.

    Args:
        embeddings: Bedrock embeddings client (needed for queries)
        path: Directory containing index files

    Returns:
        FAISS vector store
    """
    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True  # Safe - we created this index
    )


def get_or_create_vector_store(force_rebuild: bool = False) -> FAISS:
    """
    Load existing vector store or create new one.

    This is the main entry point for getting the vector store.

    Args:
        force_rebuild: If True, rebuild even if index exists

    Returns:
        FAISS vector store ready for queries
    """
    log("Starting get_or_create_vector_store...")
    log(f"FAISS_INDEX_PATH: {FAISS_INDEX_PATH}")

    embeddings = get_embeddings()
    log("Embeddings client created")

    # Check if index exists
    index_exists = (FAISS_INDEX_PATH / "index.faiss").exists()
    log(f"Index exists: {index_exists}")

    if index_exists and not force_rebuild:
        log("Loading existing vector store...")
        try:
            vs = load_vector_store(embeddings)
            log("Vector store loaded successfully")
            return vs
        except Exception as e:
            log(f"ERROR: Failed to load vector store: {e}")
            raise

    # Build new index
    log("Creating new vector store...")
    courses = load_courses()
    documents = create_documents(courses)
    vector_store = build_vector_store(documents, embeddings)
    save_vector_store(vector_store)

    return vector_store


class CourseRetriever:
    """
    Retriever with optional metadata filtering.

    FAISS doesn't support native filtering, so we implement
    post-retrieval filtering. This works well for small datasets
    like our 74 courses.

    Usage:
        retriever = CourseRetriever()

        # Semantic search only
        results = retriever.search("machine learning courses")

        # With department filter
        results = retriever.search("databases", department="Computer Science")

        # With level filter
        results = retriever.search("AI", level="Graduate")
    """

    def __init__(self, vector_store: Optional[FAISS] = None):
        """
        Initialize retriever.

        Args:
            vector_store: Optional pre-loaded vector store
        """
        self.vector_store = vector_store or get_or_create_vector_store()

    def search(
        self,
        query: str,
        k: int = RETRIEVER_K,
        department: Optional[str] = None,
        level: Optional[str] = None,
    ) -> list[Document]:
        """
        Search for relevant courses with optional filtering.

        Args:
            query: Natural language search query
            k: Number of results to return
            department: Optional filter (e.g., "Computer Science", "Statistics")
            level: Optional filter (e.g., "First Year", "Graduate")

        Returns:
            List of matching Document objects
        """
        # Over-fetch if filtering to ensure we get enough results
        fetch_k = k * 5 if (department or level) else k
        fetch_k = min(fetch_k, 74)  # Can't fetch more than we have

        # Semantic search
        results = self.vector_store.similarity_search(query, k=fetch_k)

        # Apply filters
        if department:
            results = [r for r in results if r.metadata["department"] == department]
        if level:
            results = [r for r in results if r.metadata["level"] == level]

        return results[:k]

    def search_with_scores(
        self,
        query: str,
        k: int = RETRIEVER_K,
    ) -> list[tuple[Document, float]]:
        """
        Search and return similarity scores.

        Useful for debugging and understanding relevance.

        Args:
            query: Natural language search query
            k: Number of results to return

        Returns:
            List of (Document, score) tuples. Lower score = more similar.
        """
        return self.vector_store.similarity_search_with_score(query, k=k)


# Convenience function for quick testing
def quick_search(query: str, k: int = 4) -> list[dict]:
    """
    Quick search function for testing.

    Args:
        query: Search query
        k: Number of results

    Returns:
        List of course info dictionaries
    """
    retriever = CourseRetriever()
    results = retriever.search(query, k=k)

    return [
        {
            "course_code": doc.metadata["course_code"],
            "title": doc.metadata["title"],
            "department": doc.metadata["department"],
            "level": doc.metadata["level"],
        }
        for doc in results
    ]


if __name__ == "__main__":
    # Build the vector store when run directly
    print("=" * 50)
    print("UBC Course Advisor - Vector Store Builder")
    print("=" * 50)

    # Force rebuild to ensure fresh index
    vector_store = get_or_create_vector_store(force_rebuild=True)

    # Test retrieval
    print("\n" + "=" * 50)
    print("Testing Retrieval")
    print("=" * 50)

    retriever = CourseRetriever(vector_store)

    test_queries = [
        ("machine learning", None, None),
        ("databases", "Computer Science", None),
        ("statistics", None, "Third Year"),
        ("neural networks deep learning", None, None),
    ]

    for query, dept, level in test_queries:
        print(f"\nQuery: '{query}'", end="")
        if dept:
            print(f" | Department: {dept}", end="")
        if level:
            print(f" | Level: {level}", end="")
        print()

        results = retriever.search(query, k=3, department=dept, level=level)

        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata['course_code']}: {doc.metadata['title']}")
