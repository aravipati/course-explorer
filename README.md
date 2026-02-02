# Course Explorer

A RAG-powered course discovery tool demonstrating semantic search and AI recommendations.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-red)

**Live Demo:** [cloudllm.tech](https://cloudllm.tech)

> **Disclaimer:** This is a portfolio project for demonstration purposes. Not affiliated with UBC. Course data sourced from [UBC Academic Calendar](https://vancouver.calendar.ubc.ca/course-descriptions).

## What It Does

Ask questions like:
- "I'm a beginner interested in machine learning"
- "What database courses are available?"
- "I want to prepare for AI research"

The advisor searches 74 courses semantically and provides personalized recommendations with prerequisites and course progressions.

## Architecture

```
User Query → Semantic Search (FAISS) → Relevant Courses → Claude 3.5 → Response
```

**Tech Stack:**
- **LLM:** Claude 3.5 Haiku via AWS Bedrock
- **Embeddings:** Amazon Titan Text Embeddings V2
- **Vector Store:** FAISS (Facebook AI Similarity Search)
- **Framework:** LangChain + Streamlit
- **Deployment:** AWS EC2

## Quick Start

### Prerequisites
- Python 3.11+
- AWS account with Bedrock access
- AWS CLI configured with SSO

### Installation

```bash
# Clone the repo
git clone https://github.com/aravipati/course-explorer.git
cd course-explorer

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
│   └── courses.json       # 74 courses
├── faiss_index/           # Pre-built vector index
└── Dockerfile             # Container config
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

### EC2 Deployment

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install dependencies
sudo yum install python3.11 python3.11-pip git -y

# Clone and setup
git clone https://github.com/aravipati/course-explorer.git
cd course-explorer
pip3.11 install -r requirements.txt

# Run with systemd (recommended)
sudo systemctl start streamlit
```

### Local Docker

```bash
docker build -t course-explorer .
docker run -p 8501:8501 -e AWS_REGION=us-west-2 course-explorer
```

## Cost Estimate

| Component | Monthly Cost |
|-----------|--------------|
| EC2 t3.small | ~$15 |
| Bedrock Claude (1000 queries) | ~$1 |
| Bedrock Titan Embeddings | ~$0.01 |
| **Total** | **~$16/month** |

## License

MIT

## Acknowledgments

- Course data from [UBC Academic Calendar](https://vancouver.calendar.ubc.ca/course-descriptions)
- Built with [LangChain](https://langchain.com/) and [Streamlit](https://streamlit.io/)
