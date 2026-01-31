# Architecture

This document explains how the UBC Course Advisor works under the hood.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Request Flow                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   User: "I want to learn machine learning"                           │
│                          │                                           │
│                          ▼                                           │
│   ┌──────────────────────────────────────┐                           │
│   │           Streamlit UI               │                           │
│   │           (app.py)                   │                           │
│   └──────────────────┬───────────────────┘                           │
│                      │                                               │
│                      ▼                                               │
│   ┌──────────────────────────────────────┐                           │
│   │         CourseAdvisor                │                           │
│   │         (src/rag.py)                 │                           │
│   └──────────────────┬───────────────────┘                           │
│                      │                                               │
│          ┌───────────┴───────────┐                                   │
│          ▼                       ▼                                   │
│   ┌─────────────┐         ┌─────────────┐                            │
│   │  Retriever  │         │   Claude    │                            │
│   │  (FAISS)    │────────►│   (LLM)     │                            │
│   └─────────────┘         └─────────────┘                            │
│          │                       │                                   │
│          ▼                       ▼                                   │
│   4 relevant courses      Response with                              │
│                           recommendations                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Vector Store (`src/embeddings.py`)

**Purpose:** Convert courses to searchable vectors and find relevant courses.

**How it works:**
1. Each course description is sent to Amazon Titan Embeddings
2. Titan returns a 1024-dimensional vector representing the meaning
3. All vectors are stored in a FAISS index
4. At query time, the user's question is embedded and FAISS finds the closest vectors

**Key classes:**
- `CourseRetriever`: Handles semantic search with optional filters

```python
retriever = CourseRetriever()
results = retriever.search("machine learning", department="Computer Science")
```

**Why FAISS?**
- Fast similarity search (sub-millisecond for 74 courses)
- No external database needed
- Index is just two files (~350KB total)

**Filtering:**
FAISS only does vector similarity, so filtering is done post-retrieval:
1. Fetch 5x more results than needed
2. Filter by metadata (department, level)
3. Return top K

### 2. RAG Pipeline (`src/rag.py`)

**Purpose:** Combine retrieval with Claude to generate grounded responses.

**How it works:**
1. Retrieve relevant courses using the vector store
2. Format courses into a context string
3. Send context + question to Claude
4. Claude generates a response using only the provided courses

**Key classes:**
- `CourseAdvisor`: Main interface for asking questions

```python
advisor = CourseAdvisor()
result = advisor.ask("What ML courses should I take?")
print(result["answer"])
```

**Prompt engineering:**
The system prompt instructs Claude to:
- Only recommend courses from the provided context
- Always cite course codes
- Consider prerequisites
- Be honest if no relevant courses exist

### 3. Streamlit UI (`app.py`)

**Purpose:** Provide a chat interface for users.

**Key features:**
- Chat history with session state
- Sidebar filters for department/level
- Example queries for new users
- Cached advisor to avoid reloading index

**Session state:**
```python
st.session_state.messages = []              # Display history
st.session_state.conversation_history = []  # RAG context
```

### 4. Configuration (`src/config.py`)

**Purpose:** Centralize all settings.

```python
AWS_REGION = "us-west-2"
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
LLM_MODEL_ID = "anthropic.claude-3-5-haiku-20241022-v1:0"
RETRIEVER_K = 4  # Number of courses to retrieve
```

## Data Flow

### Building the Index (one-time)

```
courses.json → create_documents() → Titan Embeddings → FAISS index
                                          │
                                          ▼
                                    faiss_index/
                                    ├── index.faiss
                                    └── index.pkl
```

### Query Processing

```
User Question
     │
     ▼
┌────────────────┐
│ Embed question │ → Titan Embeddings API
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ FAISS search   │ → Find 4 most similar courses
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Format context │ → "Course 1: CPSC 340..."
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Claude prompt  │ → System prompt + context + question
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Generate       │ → Claude 3.5 Haiku API
└────────┬───────┘
         │
         ▼
Response with recommendations + citations
```

## AWS Services Used

| Service | Purpose | Model/Config |
|---------|---------|--------------|
| Bedrock | LLM & Embeddings | Claude 3.5 Haiku, Titan V2 |
| App Runner | Hosting | 1 vCPU, 2GB RAM |

## Key Design Decisions

### Why RAG instead of fine-tuning?
- Course data changes (new courses, updated prereqs)
- RAG lets us update data without retraining
- Responses are grounded and verifiable

### Why FAISS instead of a vector database?
- 74 courses is tiny - no need for a managed service
- Zero infrastructure to maintain
- Index fits in memory easily

### Why Claude 3.5 Haiku?
- Fast (1-2 second responses)
- Cheap (~$0.001 per query)
- Sufficient quality for recommendations
- Easy upgrade path to larger models

### Why Streamlit?
- Rapid prototyping (~150 lines of code)
- Native chat components
- Easy deployment
- Good enough for portfolio/demo

## Extending the Project

### Adding more courses
1. Update `data/courses.json`
2. Rebuild index: `python -m src.embeddings`
3. Redeploy

### Adding new filters
1. Add metadata field to `create_documents()` in `embeddings.py`
2. Add filter parameter to `CourseRetriever.search()`
3. Add UI control in `app.py`

### Switching vector stores
Replace FAISS with Pinecone/Weaviate in `embeddings.py`:
1. Update `build_vector_store()` to use new store
2. Update `CourseRetriever` to use new query API
3. Remove `faiss_index/` from repo

### Switching LLMs
Update `LLM_MODEL_ID` in `config.py` to use:
- Claude 3.5 Sonnet (better quality, higher cost)
- Claude 3 Opus (best quality, highest cost)
