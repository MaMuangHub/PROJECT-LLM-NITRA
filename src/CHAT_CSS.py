"""
Enhanced RAG Chat with Beautiful CSS Styling
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import LLMClient, SimpleRAGSystem, get_available_models, load_sample_documents_for_demo


def apply_custom_css():
    """Apply beautiful custom CSS styling"""
    st.markdown("""
        <style>
        /* Main App Background */
        .stApp {
            background: linear-gradient(135deg, #1e3c72 0%, #800080 100%);
        }
        
        /* Title Styling */
        h1 {
            color: white !important;
            text-align: center;
            font-size: 3rem !important;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            margin-bottom: 0.5rem !important;
        }
        
        /* Subtitle */
        .subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        
        /* Chat Messages */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px !important;
            padding: 20px !important;
            margin: 10px 0 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        }
        
        /* User Message */
        [data-testid="stChatMessageContent"] {
            background: transparent !important;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: white !important;
        }
        
        [data-testid="stSidebar"] label {
            color: rgba(255,255,255,0.9) !important;
        }
        
        /* Input Fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            background: rgba(255,255,255,0.1);
            color: white;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 10px;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 5px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Success/Info/Warning Messages */
        .stSuccess, .stInfo, .stWarning {
            background: rgba(255,255,255,0.95) !important;
            border-radius: 10px !important;
            padding: 15px !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            color: white !important;
        }
        
        /* Card Style */
        .info-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            color: white;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .info-card h2 {
            color: white !important;
            margin-top: 0;
        }
        
        /* Chat Input */
        .stChatInput {
            border-radius: 25px;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.1);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.3);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.5);
        }
        </style>
    """, unsafe_allow_html=True)


def create_header():
    """Create beautiful header"""
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1>🤖 RAG Chat Assistant</h1>
            <p class="subtitle">
                ✨ AI-Powered Document Intelligence • Ask Anything About Your Knowledge Base
            </p>
        </div>
    """, unsafe_allow_html=True)


def create_welcome_card():
    """Create welcome card"""
    st.markdown("""
        <div class="info-card">
            <h2>🚀 Welcome to RAG Chat</h2>
            <p>
                Upload your documents and start asking questions! 
                Our AI assistant will search through your knowledge base 
                and provide accurate, context-aware answers.
            </p>
            <ul style="margin-top: 15px;">
                <li>📄 Upload PDF and text files</li>
                <li>🔍 Intelligent semantic search</li>
                <li>💡 Context-aware AI responses</li>
                <li>📚 Manage your knowledge base</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = None
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None
    if "rag_initialized" not in st.session_state:
        st.session_state.rag_initialized = False


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("context_used", False):
                st.markdown("📚 *Used document context*")
            st.markdown(message["content"])


def main():
    st.set_page_config(
        page_title="RAG Chat Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    apply_custom_css()

    # Create header
    create_header()

    # Initialize session state
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # Model selection
        available_models = get_available_models()
        selected_model = st.selectbox(
            "🤖 Select Model",
            available_models,
            index=0
        )

        temperature = st.slider("🌡️ Temperature", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.slider("📏 Max Tokens", 50, 4000, 2000, 50)

        st.divider()

        # Initialize buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🤖 Init Model"):
                with st.spinner("Loading..."):
                    st.session_state.llm_client = LLMClient(
                        model=selected_model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                st.success("✅ Ready!")

        with col2:
            if st.button("📚 Init RAG"):
                with st.spinner("Loading..."):
                    st.session_state.rag_system = SimpleRAGSystem()
                    if not st.session_state.rag_initialized:
                        load_sample_documents_for_demo(st.session_state.rag_system)
                        st.session_state.rag_initialized = True
                st.success("✅ Ready!")

        st.divider()

        # Quick actions
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("📖 Load Sample Docs") and st.session_state.rag_system:
            st.success("✅ Samples loaded!")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # Stats
        if st.session_state.rag_system:
            stats = st.session_state.rag_system.get_stats()
            st.markdown("### 📊 Statistics")
            st.metric("Documents", stats.get("total_documents", 0))
            st.metric("Chunks", stats.get("total_chunks", 0))

    # Main content
    if not st.session_state.llm_client or not st.session_state.rag_system:
        create_welcome_card()
        st.warning("⚠️ Please initialize Model and RAG system in the sidebar")
        return

    # Display chat
    display_chat_messages()

    # Example queries
    st.markdown("### 💡 Try these:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧠 What is AI?"):
            st.session_state.example_query = "What is artificial intelligence?"
    
    with col2:
        if st.button("🤖 About LLMs"):
            st.session_state.example_query = "Explain large language models"
    
    with col3:
        if st.button("🌟 About Streamlit"):
            st.session_state.example_query = "What is Streamlit?"

    # Chat input
    prompt = st.chat_input("💬 Ask me anything...")

    # Handle example query
    if hasattr(st.session_state, 'example_query'):
        prompt = st.session_state.example_query
        delattr(st.session_state, 'example_query')

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching and generating..."):
                # Get context
                context = st.session_state.rag_system.get_context_for_query(
                    prompt, max_context_length=2000
                )

                # Create prompt
                enhanced_prompt = f"""
                Based on the following context:

                {context}

                Question: {prompt}

                Provide a comprehensive answer based on the context above.
                """

                # Get response
                messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages[:-1]
                ]
                messages.append({"role": "user", "content": enhanced_prompt})

                response = st.session_state.llm_client.chat(messages)
                st.markdown(response)

                with st.expander("📄 View Context"):
                    st.markdown(context)

                # Save response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "context_used": True
                })


if __name__ == "__main__":
    main()