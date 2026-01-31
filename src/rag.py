"""
RAG (Retrieval-Augmented Generation) Pipeline for UBC Course Advisor.

This module connects the retriever to Claude to generate intelligent
course recommendations with citations.

Architecture:
    User Query → Retriever → Relevant Courses → Claude → Response with Citations

Key Components:
    - CourseAdvisor: Main RAG class combining retrieval + generation
    - Prompt templates: Structured prompts for consistent responses
    - Source citations: Every recommendation references actual courses
"""

from typing import Optional

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.documents import Document

from src.config import AWS_REGION, LLM_MODEL_ID, RETRIEVER_K
from src.embeddings import CourseRetriever


# System prompt defines Claude's persona and behavior
SYSTEM_PROMPT = """You are a helpful UBC Course Advisor assistant. Your role is to help students find the right courses based on their interests, goals, and background.

IMPORTANT RULES:
1. ONLY recommend courses from the provided context. Never make up courses.
2. Always cite course codes (e.g., CPSC 340) when mentioning courses.
3. Consider prerequisites when making recommendations.
4. Be encouraging but realistic about course difficulty.
5. If the context doesn't contain relevant courses, say so honestly.

When recommending courses:
- Explain WHY each course fits the student's needs
- Mention prerequisites if relevant
- Suggest a logical order if recommending multiple courses
- Note the course level (First Year, Graduate, etc.) to set expectations

Keep responses concise but informative. Use bullet points for multiple recommendations."""


def get_llm() -> ChatBedrock:
    """
    Initialize Claude via Bedrock.

    Returns:
        ChatBedrock client configured for Claude 3.5 Haiku
    """
    return ChatBedrock(
        model_id=LLM_MODEL_ID,
        region_name=AWS_REGION,
        model_kwargs={
            "max_tokens": 1024,
            "temperature": 0.3,  # Lower = more focused responses
        },
    )


def format_context(documents: list[Document]) -> str:
    """
    Format retrieved documents into context for the LLM.

    Args:
        documents: List of retrieved course documents

    Returns:
        Formatted string with course information
    """
    if not documents:
        return "No relevant courses found in the database."

    context_parts = []
    for i, doc in enumerate(documents, 1):
        meta = doc.metadata
        context_parts.append(f"""
Course {i}: {meta['course_code']} - {meta['title']}
Department: {meta['department']} | Level: {meta['level']} | Credits: {meta['credits']}
Prerequisites: {meta['prerequisites']}
Description: {doc.page_content.split('Description: ')[1].split('Prerequisites:')[0].strip()}
""")

    return "\n".join(context_parts)


def format_sources(documents: list[Document]) -> str:
    """
    Format sources for citation at end of response.

    Args:
        documents: List of retrieved course documents

    Returns:
        Formatted citation string
    """
    if not documents:
        return ""

    sources = []
    for doc in documents:
        meta = doc.metadata
        sources.append(f"- {meta['course_code']}: {meta['title']} ({meta['level']})")

    return "\n**Sources:**\n" + "\n".join(sources)


class CourseAdvisor:
    """
    RAG-powered course recommendation system.

    Combines semantic retrieval with Claude to provide intelligent,
    context-aware course recommendations.

    Usage:
        advisor = CourseAdvisor()

        # Simple query
        response = advisor.ask("What ML courses should I take?")

        # With filters
        response = advisor.ask(
            "I want to learn AI",
            department="Computer Science",
            level="Third Year"
        )

        # With conversation history
        response = advisor.ask(
            "What about more advanced options?",
            history=[
                ("What ML courses should I take?", "I recommend CPSC 330...")
            ]
        )
    """

    def __init__(
        self,
        retriever: Optional[CourseRetriever] = None,
        llm: Optional[ChatBedrock] = None,
    ):
        """
        Initialize the Course Advisor.

        Args:
            retriever: Optional pre-configured retriever
            llm: Optional pre-configured LLM
        """
        self.retriever = retriever or CourseRetriever()
        self.llm = llm or get_llm()

    def ask(
        self,
        question: str,
        k: int = RETRIEVER_K,
        department: Optional[str] = None,
        level: Optional[str] = None,
        history: Optional[list[tuple[str, str]]] = None,
        include_sources: bool = True,
    ) -> dict:
        """
        Ask the advisor a question about courses.

        Args:
            question: User's question in natural language
            k: Number of courses to retrieve for context
            department: Optional department filter
            level: Optional level filter
            history: Optional conversation history as [(user_msg, ai_msg), ...]
            include_sources: Whether to append source citations

        Returns:
            dict with keys:
                - answer: The generated response
                - sources: List of source documents
                - context: The formatted context sent to LLM
        """
        # Step 1: Retrieve relevant courses
        documents = self.retriever.search(
            query=question,
            k=k,
            department=department,
            level=level,
        )

        # Step 2: Format context
        context = format_context(documents)

        # Step 3: Build messages
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Add conversation history if provided
        if history:
            for user_msg, ai_msg in history:
                messages.append(HumanMessage(content=user_msg))
                messages.append(AIMessage(content=ai_msg))

        # Add current question with context
        user_prompt = f"""Based on the following UBC courses, please help answer the student's question.

AVAILABLE COURSES:
{context}

STUDENT'S QUESTION: {question}

Provide a helpful response recommending relevant courses from the list above."""

        messages.append(HumanMessage(content=user_prompt))

        # Step 4: Generate response
        response = self.llm.invoke(messages)
        answer = response.content

        # Step 5: Add sources if requested
        if include_sources and documents:
            answer += "\n\n" + format_sources(documents)

        return {
            "answer": answer,
            "sources": documents,
            "context": context,
        }

    def get_course_info(self, course_code: str) -> Optional[dict]:
        """
        Get detailed information about a specific course.

        Args:
            course_code: The course code (e.g., "CPSC 340")

        Returns:
            Course info dict or None if not found
        """
        # Search for the specific course
        results = self.retriever.search(course_code, k=5)

        for doc in results:
            if doc.metadata["course_code"].upper() == course_code.upper():
                return {
                    "course_code": doc.metadata["course_code"],
                    "title": doc.metadata["title"],
                    "description": doc.page_content,
                    "department": doc.metadata["department"],
                    "level": doc.metadata["level"],
                    "credits": doc.metadata["credits"],
                    "prerequisites": doc.metadata["prerequisites"],
                }

        return None


def quick_ask(question: str) -> str:
    """
    Convenience function for quick questions.

    Args:
        question: User's question

    Returns:
        Answer string
    """
    advisor = CourseAdvisor()
    result = advisor.ask(question)
    return result["answer"]


if __name__ == "__main__":
    print("=" * 60)
    print("UBC Course Advisor - RAG Pipeline Test")
    print("=" * 60)

    advisor = CourseAdvisor()

    # Test queries
    test_queries = [
        {
            "question": "I'm a beginner interested in machine learning. What courses should I start with?",
            "filters": {},
        },
        {
            "question": "What database courses are available?",
            "filters": {"department": "Computer Science"},
        },
        {
            "question": "I want to do AI research. What graduate courses should I consider?",
            "filters": {"level": "Graduate"},
        },
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test['question']}")
        if test['filters']:
            print(f"Filters: {test['filters']}")
        print("=" * 60)

        result = advisor.ask(test['question'], **test['filters'])
        print(result['answer'])
