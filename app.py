"""
Course Explorer - Streamlit Application

A RAG-powered chatbot demo that helps explore course catalogs
using semantic search and AI recommendations.

This is a portfolio project demonstrating RAG architecture.

Run locally:
    streamlit run app.py

Architecture:
    Streamlit UI → CourseAdvisor (RAG) → Bedrock (Claude + Titan)
"""

import streamlit as st
import sys

# Use print with flush for immediate output in App Runner
def log(msg):
    print(f"[APP] {msg}", flush=True)
    sys.stdout.flush()

log("Starting Course Explorer app...")

from src.config import PAGE_TITLE, PAGE_ICON
log("Config loaded")

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="centered",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_advisor():
    """
    Initialize CourseAdvisor with caching.

    Uses st.cache_resource to avoid reloading the vector store
    on every interaction.
    """
    log("Initializing CourseAdvisor...")
    try:
        log("Importing CourseAdvisor...")
        from src.rag import CourseAdvisor
        log("CourseAdvisor imported, creating instance...")
        advisor = CourseAdvisor()
        log("CourseAdvisor initialized successfully")
        return advisor
    except Exception as e:
        log(f"ERROR: Failed to initialize CourseAdvisor: {e}")
        import traceback
        traceback.print_exc()
        raise


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []


def render_sidebar():
    """Render the sidebar with filters and info."""
    with st.sidebar:
        st.header("Filters")

        # Department filter
        department = st.selectbox(
            "Department",
            options=[
                "All Departments",
                "Computer Science",
                "Statistics",
                "Mathematics",
                "Data Science",
            ],
            index=0,
        )

        # Level filter
        level = st.selectbox(
            "Course Level",
            options=[
                "All Levels",
                "First Year",
                "Second Year",
                "Third Year",
                "Fourth Year",
                "Graduate",
            ],
            index=0,
        )

        st.divider()

        # Info section
        st.header("About")
        st.markdown("""
        An AI-powered course discovery tool using RAG (Retrieval-Augmented Generation).

        **Features:**
        - Semantic search across courses
        - Prerequisite-aware recommendations
        - Filter by department or level

        **Tech Stack:**
        - AWS Bedrock (Claude 3.5 Haiku)
        - FAISS vector search
        - LangChain
        """)

        st.divider()

        # Disclaimer
        st.caption("""
        **Disclaimer:** Portfolio project for demonstration purposes.
        Not affiliated with UBC. Data sourced from [UBC Academic Calendar](https://vancouver.calendar.ubc.ca/course-descriptions).
        """)

        st.divider()

        # Clear chat button
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()

        # Convert "All" options to None for the advisor
        dept_filter = None if department == "All Departments" else department
        level_filter = None if level == "All Levels" else level

        return dept_filter, level_filter


def render_chat_message(role: str, content: str):
    """Render a single chat message."""
    with st.chat_message(role):
        st.markdown(content)


def render_chat_history():
    """Render all messages in the chat history."""
    for message in st.session_state.messages:
        render_chat_message(message["role"], message["content"])


def process_user_input(
    user_input: str,
    advisor,
    department: str | None,
    level: str | None,
):
    """Process user input and generate response."""
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    render_chat_message("user", user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching courses..."):
            result = advisor.ask(
                question=user_input,
                department=department,
                level=level,
                history=st.session_state.conversation_history,
            )

            response = result["answer"]

            # Display response
            st.markdown(response)

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Update conversation history for context
    st.session_state.conversation_history.append((user_input, response))

    # Keep only last 5 turns to avoid context overflow
    if len(st.session_state.conversation_history) > 5:
        st.session_state.conversation_history = st.session_state.conversation_history[-5:]


def render_example_queries():
    """Render example query buttons."""
    st.markdown("**Try asking:**")

    examples = [
        "I'm a beginner interested in machine learning",
        "What database courses are available?",
        "I want to prepare for AI research",
        "What are the prerequisites for CPSC 340?",
    ]

    # Track which example was clicked (if any)
    selected = None

    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                selected = example

    return selected


def main():
    """Main application entry point."""
    # Initialize session state first (fast)
    initialize_session_state()

    # Render sidebar and get filters (fast - UI only)
    department, level = render_sidebar()

    # Main content (fast - UI only)
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.markdown("*AI-powered course discovery using RAG*")

    # Show filter status if active
    if department or level:
        filter_text = []
        if department:
            filter_text.append(f"**Department:** {department}")
        if level:
            filter_text.append(f"**Level:** {level}")
        st.info(" | ".join(filter_text))

    st.divider()

    # Render chat history
    render_chat_history()

    # Show examples if no messages yet
    example_query = None
    if not st.session_state.messages:
        example_query = render_example_queries()

    # Chat input
    user_input = st.chat_input("Ask about courses...")

    # Only initialize advisor when actually needed (on user input)
    if user_input or example_query:
        # Show loading message while initializing
        with st.spinner("Initializing AI advisor..."):
            advisor = get_advisor()

        # Process input
        if user_input:
            process_user_input(user_input, advisor, department, level)
        elif example_query:
            process_user_input(example_query, advisor, department, level)
            st.rerun()  # Clean rerun to hide example buttons


if __name__ == "__main__":
    main()
