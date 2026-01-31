"""
Configuration settings for UBC Course Advisor.

Centralizes all configuration to make the app easy to modify and deploy
across different environments (local dev vs EC2 production).
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FAISS_INDEX_PATH = PROJECT_ROOT / "faiss_index"

# AWS Bedrock settings
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

# Model IDs - using inference profiles for on-demand access
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
LLM_MODEL_ID = "anthropic.claude-3-5-haiku-20241022-v1:0"

# RAG settings
RETRIEVER_K = 4  # Number of documents to retrieve
CHUNK_SIZE = 1000  # For text splitting if needed
CHUNK_OVERLAP = 200

# Streamlit settings
PAGE_TITLE = "UBC Course Advisor"
PAGE_ICON = "🎓"
