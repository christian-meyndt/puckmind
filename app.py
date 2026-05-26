"""
PuckMind - Hockey Scout & Team Manager Agent
Web UI built with Streamlit
"""

import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.agent import (
    get_all_players,
    get_available_players,
    get_top_scorers,
    get_recent_games,
    get_season_record,
    suggest_lineup,
    add_game_result,
    suggest_training_exercises,
    hockey_agent,
)

load_dotenv()

# Force use of Vertex AI
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

# Page config
st.set_page_config(
    page_title="PuckMind - Hockey Agent",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .example-query {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_session" not in st.session_state:
    st.session_state.agent_session = None
if "session_service" not in st.session_state:
    st.session_state.session_service = None
if "runner" not in st.session_state:
    st.session_state.runner = None


# Initialize agent (only once)
@st.cache_resource
def initialize_agent():
    """Initialize the agent, runner, and session."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=hockey_agent,
        app_name="hockey_agent",
        session_service=session_service,
    )
    return session_service, runner


async def create_session(session_service):
    """Create a new agent session."""
    return await session_service.create_session(
        app_name="hockey_agent",
        user_id="web_user",
    )


def get_agent_response(runner, session_id, user_message):
    """Get response from the agent."""
    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )

    events = runner.run(
        user_id="web_user",
        session_id=session_id,
        new_message=content,
    )

    for event in events:
        if event.is_final_response():
            return event.content.parts[0].text

    return "Sorry, I couldn't process that request."


# Header
st.markdown('<div class="main-header">🏒 PuckMind</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-Powered Hockey Scout & Team Manager</div>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("About PuckMind")
    st.write("""
    PuckMind is an AI agent that helps amateur hockey teams with:

    - 📊 Player statistics & availability
    - 🎯 Lineup suggestions
    - 🏆 Game results & season records
    - 🏋️ Training planning & exercises
    - 📈 Team analytics
    """)

    st.divider()

    st.header("Example Queries")

    if st.button("💬 Top forwards", use_container_width=True):
        st.session_state.trigger_query = "Show me our top forwards with offensive stats like shooting % and faceoff %"
        st.rerun()

    if st.button("💬 Top defenders", use_container_width=True):
        st.session_state.trigger_query = "Who are our best defenders? Show defensive stats like blocked shots and plus/minus"
        st.rerun()

    if st.button("💬 Goalie stats", use_container_width=True):
        st.session_state.trigger_query = "What are our goalie statistics? Show GAA and save percentage"
        st.rerun()

    if st.button("💬 Player form", use_container_width=True):
        st.session_state.trigger_query = "Who's on a hot or cold streak?"
        st.rerun()

    if st.button("💬 Suggest lineup", use_container_width=True):
        st.session_state.trigger_query = "Suggest a lineup for the next game"
        st.rerun()

    if st.button("💬 Season prediction", use_container_width=True):
        st.session_state.trigger_query = "Predict our final standing this season"
        st.rerun()

    if st.button("💬 Analyze opponent", use_container_width=True):
        st.session_state.trigger_query = "Analyze our history against EHC Eagles"
        st.rerun()

    st.divider()

    st.header("Quick Actions")

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.agent_session = None
        st.rerun()

    st.divider()

    st.write("**Built with:**")
    st.write("""
    - Google Gemini 2.5 Flash
    - MongoDB Atlas
    - Google ADK
    - Model Context Protocol (MCP)
    """)

# Initialize agent if not already done
if st.session_state.session_service is None:
    with st.spinner("Initializing PuckMind..."):
        session_service, runner = initialize_agent()
        st.session_state.session_service = session_service
        st.session_state.runner = runner

        # Create session
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agent_session = loop.run_until_complete(create_session(session_service))
        st.session_state.agent_session = agent_session

# Main chat interface
st.subheader("Chat with your Hockey Agent")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle triggered query from example buttons
if st.session_state.get("trigger_query"):
    prompt = st.session_state.trigger_query
    st.session_state.trigger_query = None

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_agent_response(
                st.session_state.runner,
                st.session_state.agent_session.id,
                prompt
            )
            st.markdown(response)

    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

# Chat input
if prompt := st.chat_input("Ask about your team..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_agent_response(
                st.session_state.runner,
                st.session_state.agent_session.id,
                prompt
            )
            st.markdown(response)

    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Built for the Google Cloud Rapid Agent Hackathon |
    <a href="https://github.com/christian-meyndt/puckmind" target="_blank">GitHub</a> |
    Powered by Google Gemini & MongoDB
</div>
""", unsafe_allow_html=True)
