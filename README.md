# UBC Course Advisor

An AI-powered chatbot that helps UBC students find the right courses using natural language queries.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-red)

## What It Does

Ask questions like:
- "I'm a beginner interested in machine learning"
- "What database courses are available?"
- "I want to prepare for AI research"

The advisor searches 74 UBC courses semantically and provides personalized recommendations with prerequisites and course progressions.

## Architecture

```
User Query → Semantic Search (FAISS) → Relevant Courses → Claude 3.5 → Response
```

**Tech Stack:**
- **LLM:** Claude 3.5 Haiku via AWS Bedrock
- **Embeddings:** Amazon Titan Text Embeddings V2
- **Vector Store:** FAISS (Facebook AI Similarity Search)
- **Framework:** LangChain + Streamlit
- **Deployment:** AWS App Runner

## Quick Start

### Prerequisites
- Python 3.11+
- AWS account with Bedrock access
- AWS CLI configured with SSO

### Installation

```bash
# Clone the repo
git clone https://github.com/aravipati/ubc-course-advisor.git
cd ubc-course-advisor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Opens at http://localhost:8501

### AWS Setup

1. Enable Claude 3.5 Haiku and Titan Embeddings in [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Configure AWS CLI with SSO:
```bash
aws configure sso
aws sso login
```

## Project Structure

```
ubc-course-advisor/
├── app.py                 # Streamlit UI
├── src/
│   ├── config.py          # Configuration settings
│   ├── embeddings.py      # Vector store & retrieval
│   └── rag.py             # RAG pipeline with Claude
├── data/
│   └── courses.json       # 74 UBC courses
├── faiss_index/           # Pre-built vector index
├── Dockerfile             # Container config
└── apprunner.yaml         # AWS App Runner config
```

## How It Works

### 1. Embeddings
Course descriptions are converted to 1024-dimensional vectors using Amazon Titan. Similar courses end up close together in vector space.

### 2. Retrieval
When you ask a question, it's embedded and FAISS finds the most similar course vectors. Supports filtering by department and course level.

### 3. Generation
Retrieved courses are passed to Claude 3.5 Haiku with a prompt that ensures recommendations are grounded in actual course data.

## Features

- **Semantic Search:** Understands meaning, not just keywords
- **Filters:** Filter by department (CS, Stats, Math) or level (1st year to Graduate)
- **Citations:** Every recommendation cites actual courses
- **Conversation Memory:** Supports follow-up questions

## Deployment

### AWS App Runner (Recommended)

```bash
# Create ECR repository
aws ecr create-repository --repository-name ubc-course-advisor

# Build and push Docker image
docker build -t ubc-course-advisor .
docker tag ubc-course-advisor:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/ubc-course-advisor:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/ubc-course-advisor:latest

# Deploy via App Runner Console or CLI
```

### Local Docker

```bash
docker build -t ubc-course-advisor .
docker run -p 8501:8501 -e AWS_REGION=us-west-2 ubc-course-advisor
```

## Cost Estimate

| Component | Monthly Cost |
|-----------|--------------|
| App Runner (low traffic) | ~$5-10 |
| Bedrock Claude (1000 queries) | ~$1 |
| Bedrock Titan Embeddings | ~$0.01 |
| **Total** | **~$6-12/month** |

## License

MIT

## Acknowledgments

- Course data from [UBC Academic Calendar](https://vancouver.calendar.ubc.ca/)
- Built with [LangChain](https://langchain.com/) and [Streamlit](https://streamlit.io/)
