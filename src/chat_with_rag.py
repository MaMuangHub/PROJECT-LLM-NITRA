"""
Chat Application with RAG (Retrieval Augmented Generation)
Beautiful CSS Styling + Full Features
"""

import streamlit as st
import sys
import os
from pathlib import Path
import tempfile
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
 
from utils.rag_system import load_sample_documents, load_sample_documents_for_demo,SimpleRAGSystem
from utils.llm_client import LLMClient, get_available_models
from utils.search_tools import WebSearchTool, format_search_results

def apply_custom_css():
    """Apply beautiful custom CSS styling"""
    st.markdown("""
        <style>
        /* Main App Background */
        .stApp {
            background: linear-gradient(180deg, #282828 0%, #800080  100%);
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
            background: rgba(255, 255, 255, 0.2) !important;
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
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] .stMarkdown {
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
        
        /* Headers in main area */
        h2, h3 {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def is_sleep_related_query(query: str) -> bool:
    """Check if the query is related to sleep topics"""
    sleep_keywords = [
        # English keywords
        'sleep', 'insomnia', 'sleeping', 'sleepless', 'sleep disorder', 'sleep quality',
        'rem sleep', 'deep sleep', 'nap', 'napping', 'bedtime', 'nightmare', 'dream',
        'snore', 'snoring', 'apnea', 'sleep apnea', 'drowsy', 'drowsiness', 'tired',
        'fatigue', 'rest', 'resting', 'circadian', 'melatonin', 'wake', 'waking',
        'sleepy', 'sleepiness', 'sleep deprivation', 'sleep cycle', 'sleep pattern',
        'oversleep', 'undersleep', 'shift work', 'sleep hygiene',
        
        # Thai keywords
        'นอน', 'หลับ', 'นอนไม่หลับ', 'นอนหลับ', 'อาการนอนไม่หลับ', 'คุณภาพการนอน',
        'ความฝัน', 'ฝันร้าย', 'กรน', 'หยุดหายใจขณะหลับ', 'ง่วง', 'ง่วงนอน', 'เหนื่อย',
        'อ่อนเพลีย', 'พักผ่อน', 'จังหวะชีวิต', 'เมลาโทนิน', 'ตื่น', 'ตื่นนอน',
        'ง่วงซึม', 'พักผ่อนไม่พอ', 'วงจรการนอน', 'รูปแบบการนอน', 'นอนมาก', 'นอนน้อย',
        'สุขอนามัยการนอน', 'ชั่วโมงการนอน', 'เตียง', 'หมอน', 'ห้องนอน'
    ]

    query_lower = query.lower()
    return any(keyword in query_lower for keyword in sleep_keywords)

def execute_search(query: str, num_results: int = 5):
    """Execute web search and return formatted results"""
    results = st.session_state.search_tool.search(query, num_results)
    return format_search_results(results)

def create_header():
    """Create beautiful header"""
    import base64
    
    # อ่านรูปจาก static folder
    try:
        with open("Picture/nitra.png", "rb") as f:
            img = base64.b64encode(f.read()).decode()
        img_url = f"data:image/png;base64,{img}"
    except:
        img_url = ""  # ถ้าไม่มีรูปใช้ emoji
    
    if img_url:
        st.markdown(f"""
            <style> 
            .logo-circle {{
                width: 120px;
                height: 120px;
                margin: 0 auto 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 60%;
                box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
                animation: float 3s ease-in-out infinite;
                background-image: url('{img_url}');
                background-size: 99%;
                background-position: center;
                background-repeat: no-repeat;
            }}
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-10px); }}
            }}
            </style>
            <div style="text-align: center; padding: 20px 0;">
                <div class="logo-circle"></div>
                <h1>NITRA</h1>
                <p class="subtitle"> 🌙 NITRA — Helping you sleep better, every night.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h1>NITRA</h1>
                <p class="subtitle">🌙 NITRA — Helping you sleep better, every night</p>
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
    if "search_tool" not in st.session_state:
        st.session_state.search_tool = WebSearchTool()


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("context_used", False):
                st.markdown("📚 *Used document context*")
            if message.get("search_used", False):
                st.markdown("🔍 *Used web search*")
            st.markdown(message["content"])


def display_documents():
    """Display documents in the RAG system"""
    if st.session_state.rag_system:
        docs = st.session_state.rag_system.list_documents()

        if docs and not any("error" in doc for doc in docs):
            st.markdown("### 📄 Documents in Knowledge Base")
            for doc in docs:
                with st.expander(f"📄 {doc.get('doc_id', 'Unknown')} ({doc.get('chunks', 0)} chunks)"):
                    st.json(doc.get('metadata', {}))
                    if st.button(f"Delete {doc['doc_id']}", key=f"delete_{doc['doc_id']}"):
                        result = st.session_state.rag_system.delete_document(doc['doc_id'])
                        st.success(result)
                        st.rerun()
        else:
            st.info("No documents in knowledge base yet.")


def main():
    st.set_page_config(
        page_title="NITRA",
        page_icon="🌙",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    apply_custom_css()

    # Create header
    create_header()

    # Initialize session state
    init_session_state()

    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # Model selection
        available_models = get_available_models()
        selected_model = st.selectbox(
            "🤖 Select Model",
            available_models,
            index=0,
            help="Choose the language model to use"
        )

        # Temperature slider
        temperature = st.slider(
            "🌡️ Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in responses"
        )

        # Max tokens
        max_tokens = st.slider(
            "📏 Max Tokens",
            min_value=50,
            max_value=4000,
            value=2000,
            step=50,
            help="Maximum length of response"
        )

        # RAG settings
        st.markdown("### 📚 RAG Settings")
        context_max_tokens = st.slider(
            "Context Max Tokens",
            min_value=500,
            max_value=3000,
            value=1500,
            step=100,
            help="Maximum tokens for context"
        )

        n_results = st.slider(
            "Search Results",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of document chunks to retrieve"
        )

        # Web search settings
        st.markdown("### 🔍 Web Search Settings")
        enable_web_search = st.checkbox(
            "Enable Web Search Fallback",
            value=True,
            help="Search web when RAG doesn't have sufficient information"
        )

        web_search_results = st.slider(
            "Web Search Results",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of web search results to fetch"
        )

        st.divider()

        # Initialize systems
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🤖 Init Model") or st.session_state.llm_client is None:
                with st.spinner("Initializing model..."):
                    st.session_state.llm_client = LLMClient(
                        model=selected_model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                st.success("Model ready!")

        with col2:
            if st.button("📚 Init RAG") or st.session_state.rag_system is None:
                with st.spinner("Initializing RAG system..."):
                    st.session_state.rag_system = SimpleRAGSystem()
                    if not st.session_state.rag_initialized:
                        # Load data folder
                        load_sample_documents(st.session_state.rag_system, "./data")
                        st.session_state.rag_initialized = True
                st.success("RAG ready!")

        st.divider()

        # Document management
        st.markdown("### 📁 Document Management")

        # File upload
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["txt", "pdf"],
            accept_multiple_files=True,
            help="Upload text or PDF files to add to knowledge base"
        )

        if uploaded_files and st.session_state.rag_system:
            for uploaded_file in uploaded_files:
                if st.button(f"Add {uploaded_file.name}", key=f"add_{uploaded_file.name}"):
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name

                        try:
                            if uploaded_file.type == "application/pdf":
                                result = st.session_state.rag_system.add_pdf_document(
                                    tmp_path,
                                    uploaded_file.name.split('.')[0]
                                )
                            else:
                                # Text file
                                content = uploaded_file.getvalue().decode("utf-8")
                                st.session_state.rag_system.add_text_document(
                                    content,
                                    uploaded_file.name.split('.')[0],
                                    {"source": uploaded_file.name, "type": "uploaded"}
                                )
                                result = f"Successfully added text file: {uploaded_file.name}"

                            st.success(result)
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        finally:
                            # Clean up temp file
                            os.unlink(tmp_path)

                        st.rerun()

        # Add text document
        with st.expander("✏️ Add Text Document"):
            doc_title = st.text_input("Document Title")
            doc_content = st.text_area("Document Content", height=200)

            if st.button("Add Text Document") and doc_title and doc_content and st.session_state.rag_system:
                st.session_state.rag_system.add_text_document(
                    doc_content,
                    doc_title.lower().replace(" ", "_"),
                    {"title": doc_title, "type": "manual_entry"}
                )
                st.success(f"Added document: {doc_title}")
                st.rerun()

        # Load sample documents
        if st.button("📖 Load Sample Docs") and st.session_state.rag_system:
            result = load_sample_documents(st.session_state.rag_system)
            st.success(result)
            st.rerun()

        st.divider()

        # Quick actions
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

                # Search API status
        st.divider()
        st.markdown("### 🔍 Search API Status")
        serper_key = os.getenv("SERPER_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")
        st.write(f"**Serper** {'✅' if serper_key else '❌'}")
        st.write(f"**Tavily** {'✅' if tavily_key else '❌'}")

        st.divider()
        st.markdown("### 📚 About")
        st.markdown("""
        **Features:**
        - Upload PDF and text files 
        - Semantic search across documents
        - Contextual AI responses
        - Document management
        
        **For Students:**
        - Experiment with embeddings
        - Advanced chunking strategies
        - Metadata filtering
        - Citation systems

        **Smart Search**
        - Only searches sleep-related topics
        - Automatic fallback when RAG lacks info
        - Fetches from 5 reliable sources
        """)

    # Main interface - Two tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📄 Documents"])

    with tab1:
        # Main chat interface
        if not st.session_state.llm_client or not st.session_state.rag_system:
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
                        <li>🌐 Web search fallback for missing info</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            st.warning("⚠️ Please initialize both Model and RAG system in the sidebar first!")
            return

        # Display existing chat messages
        display_chat_messages()

        # Example queries
        st.markdown("### ❓ How do you have sleep problems today:")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💤 I feel like I can't sleep today."):
                st.session_state.example_query = "I feel like I can't sleep today."

        with col2:
            if st.button("😴 How many hours should I sleep?"):
                st.session_state.example_query = "How many hours should I sleep?"

        with col3:
            if st.button("🛏️ Tell me how to sleep well."):
                st.session_state.example_query = "Tell me how to sleep well."

        # Chat input
        prompt = st.chat_input("💬 Ask me anything about the sleep...")

        # Handle example query
        if hasattr(st.session_state, 'example_query'):
            prompt = st.session_state.example_query
            delattr(st.session_state, 'example_query')

        if prompt:

            # Display user message
            # Add user message to chat history
            with st.chat_message("user"):
                st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
           
            if not is_sleep_related_query(prompt):
                with st.chat_message("assistant"):
                    sorry_msg = "I'm sorry, but I can only answer questions related to sleep and sleep disorders. Please ask me about sleep quality, insomnia, sleep cycles, or other sleep-related topics. 😴"
                    st.markdown(sorry_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": sorry_msg,
                        "context_used": False,
                        "search_used": False
                    })
            
            if is_sleep_related_query(prompt): 

                # Generate and display assistant response
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Searching documents and generating response..."):
                        # Get relevant context from RAG system
                        context = st.session_state.rag_system.get_context_for_query(
                            prompt, max_context_length=context_max_tokens)

                        # First, try to answer with RAG
                        enhanced_prompt_rag = f"""
                        You are a highly specialized sleep expert. Answer the user's question using ONLY the information in [Context] below.

                        IMPORTANT: If the [Context] does not contain sufficient information to fully answer the question, you MUST respond with EXACTLY this phrase: "INSUFFICIENT_CONTEXT"
                
                        [Context]
                        {context}

                        User Question: {prompt}
                        """

                        # Prepare messages for LLM
                        messages = []
                        # Add conversation history (excluding current question)
                        for msg in st.session_state.messages[:-1]:
                            messages.append({"role": msg["role"], "content": msg["content"]})
                        messages.append({"role": "user", "content": enhanced_prompt_rag})

                        # Get initial response from LLM
                        initial_response = st.session_state.llm_client.chat(messages)

                        search_used = False

                        if "INSUFFICIENT_CONTEXT" in initial_response:
                            st.warning("📚RAG knowledge base not enough!!!")

                            if enable_web_search:
                                st.info("🔍Searching the web for current information...")

                                ##### Search
                                enhanced_prompt_search = prompt + "** ONLY SEARCH FROM WEBSITE THAT HAVE RESEARCH-BACKED RESOURCES ABOUT SLEEPING **"
                                search_results = execute_search(enhanced_prompt_search, web_search_results)
                                search_context = search_results
                                search_used = True

                                st.success(f"✅ Web search completed! Using {web_search_results} sources.")
                                
                                # Search prompt
                                enhanced_prompt = f"""
                                You are a highly specialized sleep expert with an exceptional ability to simplify complex topics.

                                Core Instructions:
                                1. Level of Detail & Simplicity: Your answers must be detailed and comprehensive, treating the user as a complete novice. Use simple, clear language.
                                2. **Language Match: Answer in the same language used by the user (Thai or English). Ensure natural and fluent language.**
                                3. Content Scope: Focus exclusively on sleep-related topics.
                                4. Web Search Context: Below is current information from the web. Use this to answer comprehensively.

                                [Web Search Results]
                                {search_context}

                                User Question: {prompt}

                                Please provide a comprehensive answer based on the web search results above. Synthesize information from multiple sources and present it clearly.
                                """

                                # Get new respone with web search context
                                message_web = []
                                for msg in st.session_state.messages[:-1]:
                                    message_web.append({"role": msg["role"], "content": msg["content"]})
                                message_web.append({"role": "user", "content": enhanced_prompt})

                                response = st.session_state.llm_client.chat(message_web)
                            else:
                                st.warning("⚠️ Web search is disabled. Cannot fetch additional information.")
                                response = "I don't have sufficient information in my knowledge base to answer this question. Please enable web search or add more documents to the knowledge base."
                        else:
                            # RAG is good
                            response = initial_response
                            search_context = context
                        
                        # Create enhanced prompt with context
                        if not search_used:
                            enhanced_prompt = f"""
                            You are a highly specialized sleep expert with an exceptional ability to simplify complex topics. Your sole duty is to answer user questions strictly based on the information provided in the knowledge base [Context] below.

                            Core Instructions:
                            1. Level of Detail & Simplicity: Your answers must be detailed and comprehensive, treating the user as a complete novice with zero prior knowledge of sleep science. Use simple, clear language and fully explain all core concepts.
                            2. **Language Match: Answer the user's question in the same language used by the user (e.g., Thai, English). Ensure the tone is appropriate for a specialized expert and the language is natural and fluent.**
                            3. Content Scope: Your response must focus exclusively on the topic of sleeping. This includes sleep quality, causes, health impacts, and specifically disorders or conditions caused by lack of sleep or poor sleep quality.
                            4. Context Constraint (Anti-Hallucination): You must answer using only the data in [Context]. If [Context] doesn't contain relevant information, explicitly state that the necessary information is not available and stop. Do not use external knowledge or make assumptions.

                            If you can't find the answer about sleeping, you must respond "I don't know based on my current knowledge base."

                            [Context]
                            {context}

                            User Question: {prompt}
                            """

                        # Prepare messages for LLM
                        messages = []
                        # Add conversation history (excluding current question)
                        for msg in st.session_state.messages[:-1]:
                            messages.append({"role": msg["role"], "content": msg["content"]})

                        # Add the enhanced prompt
                        messages.append({"role": "user", "content": enhanced_prompt})

                        # Get response from LLM
                        response = st.session_state.llm_client.chat(messages)

                        # Display response
                        st.markdown(response)

                        # Show retrieved context in expander
                        if search_used:
                            with st.expander("🌐 Web Search Results"):
                                st.markdown(search_context)
                        else:
                            with st.expander("📄 Retrieved Context"):
                                st.markdown(context)

                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "context_used": True,
                            "search_used": search_used
                        })

        with tab2:
            # Document management tab
            display_documents()


if __name__ == "__main__":
    main()