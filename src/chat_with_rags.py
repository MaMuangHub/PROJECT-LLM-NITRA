import streamlit as st
import sys
import os
import tempfile
import base64
from pathlib import Path
from PIL import Image

# Add project root to path
# NOTE: Assumes chat_re.py is inside the 'src' folder.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import utilities from the project root (Ensure utils.py is in the project root)
from utils import SimpleRAGSystem, load_sample_documents, load_sample_documents_for_demo
from utils.llm_client import LLMClient, get_available_models
from utils.search_tools import WebSearchTool, format_search_results

# Import language texts
from interface_thai import get_texts # <-- ดึงฟังก์ชัน get_texts


def load_css(file_name):
    """Loads a CSS file and injects it into Streamlit."""
    try:
        css_path = Path(__file__).parent / file_name
        
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: Could not find CSS file '{file_name}' at {css_path}")


def apply_custom_css():
    """Apply custom CSS styling by loading from an external file"""
    # NOTE: Assuming the CSS file is named 'style.css' based on your last input
    load_css("style.css")


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


def create_header(texts): 
    """Create beautiful header, fixed image path"""
    
    # NEW: Calculate image path relative to the script's location
    # Assumes image is at project_root/Picture/nitra.png
    image_path = Path(__file__).parent.parent / "Picture" / "nitra.png"
    
    # Read image and convert to base64
    try:
        with open(image_path, "rb") as f:
            img = base64.b64encode(f.read()).decode()
        img_url = f"data:image/png;base64,{img}"
    except Exception as e:
        # Fallback if image not found (uses default styling/no logo)
        img_url = "" 
    
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
                <h1>{texts["HEADER_TITLE"]}</h1> 
                <p class="subtitle"> {texts["HEADER_SUBTITLE"]}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback header if image fails to load
        st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h1>{texts["HEADER_TITLE"]}</h1>
                <p class="subtitle">{texts["HEADER_SUBTITLE"]}</p>
            </div>
        """, unsafe_allow_html=True)
    

def init_session_state():
    """Initialize session state variables, including language"""
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
    if "language" not in st.session_state: 
        st.session_state.language = "th" # Default to Thai

    
def display_chat_messages(texts):
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("context_used", False) and not message.get("search_used", False):
                st.markdown(texts["CONTEXT_USED"])
            if message.get("search_used", False):
                st.markdown(texts["SEARCH_USED"])
            st.markdown(message["content"])


def display_documents(texts):
    """Display documents in the RAG system"""
    if st.session_state.rag_system:
        docs = st.session_state.rag_system.list_documents()

        if docs and not any("error" in doc for doc in docs):
            st.markdown(f"### {texts['DOC_KB_HEADER']}")
            for doc in docs:
                with st.expander(f"📄 {doc.get('doc_id', 'Unknown')} ({doc.get('chunks', 0)} chunks)"):
                    st.json(doc.get('metadata', {}))
                    
                    delete_button_label = f"{texts['DELETE_BUTTON_LABEL']} {doc['doc_id']}"
                    
                    if st.button(delete_button_label, key=f"delete_{doc['doc_id']}"):
                        result = st.session_state.rag_system.delete_document(doc['doc_id'])
                        st.success(result)
                        st.rerun()
        else:
            st.info(texts["NO_DOCS_INFO"])


def main():
    # Initialize session state first
    init_session_state()
    
    # Get texts based on current language
    texts = get_texts(st.session_state.language) 
    
    st.set_page_config(
        page_title=texts["APP_TITLE"],
        page_icon="🌙",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    apply_custom_css()

    # Language toggle button in top-right corner 
    col1, col2 = st.columns([6, 1])
    with col2:
        # Check if the button label is from the correct language file
        lang_button_label = texts.get("LANG_BUTTON", "Toggle Language")
        if st.button(lang_button_label, key="lang_toggle"):
            st.session_state.language = "en" if st.session_state.language == "th" else "th"
            st.rerun()

    # Create header
    create_header(texts)

    # Sidebar configuration
    with st.sidebar:
        st.markdown(f"### {texts['SIDEBAR_CONFIG_HEADER']}")

        # Model selection
        available_models = get_available_models()
        selected_model = st.selectbox(
            texts["MODEL_SELECT_LABEL"],
            available_models,
            index=0,
            help=texts["MODEL_SELECT_HELP"]
        )

        # Temperature slider
        temperature = st.slider(
            texts["TEMP_SLIDER_LABEL"],
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help=texts["TEMP_SLIDER_HELP"]
        )

        # Max tokens
        max_tokens = st.slider(
            texts["MAX_TOKENS_LABEL"],
            min_value=50,
            max_value=4000,
            value=2000,
            step=50,
            help=texts["MAX_TOKENS_HELP"]
        )

        # RAG settings
        st.markdown(f"### {texts['RAG_SETTINGS_HEADER']}")
        context_max_tokens = st.slider(
            texts["CONTEXT_MAX_TOKENS_LABEL"],
            min_value=500,
            max_value=3000,
            value=1500,
            step=100,
            help=texts["CONTEXT_MAX_TOKENS_HELP"]
        )

        n_results = st.slider(
            texts["SEARCH_RESULTS_LABEL"],
            min_value=1,
            max_value=10,
            value=5,
            help=texts["SEARCH_RESULTS_HELP"]
        )

        # Web search settings
        st.markdown(f"### {texts['WEB_SETTINGS_HEADER']}")
        enable_web_search = st.checkbox(
            texts["WEB_ENABLE_LABEL"],
            value=True,
            help=texts["WEB_ENABLE_HELP"]
        )

        web_search_results = st.slider(
            texts["WEB_SEARCH_RESULTS_LABEL"],
            min_value=1,
            max_value=10,
            value=5,
            help=texts["WEB_SEARCH_RESULTS_HELP"]
        )

        st.divider()

        # Initialize systems
        col1, col2 = st.columns(2)

        with col1:
            if st.button(texts["INIT_MODEL_BUTTON"]) or st.session_state.llm_client is None:
                with st.spinner(texts["INIT_MODEL_SPINNER"]): 
                    st.session_state.llm_client = LLMClient(
                        model=selected_model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                st.success(texts["INIT_MODEL_SUCCESS"])

        with col2:
            if st.button(texts["INIT_RAG_BUTTON"]) or st.session_state.rag_system is None:
                with st.spinner(texts["INIT_RAG_SPINNER"]): 
                    st.session_state.rag_system = SimpleRAGSystem()
                    if not st.session_state.rag_initialized:
                        load_sample_documents(st.session_state.rag_system, "./data")
                        st.session_state.rag_initialized = True
                st.success(texts["INIT_RAG_SUCCESS"])

        st.divider()

        # Document management
        st.markdown(f"### {texts['DOC_MANAGEMENT_HEADER']}")

        # File upload
        uploaded_files = st.file_uploader(
            texts["FILE_UPLOADER_LABEL"],
            type=["txt", "pdf"],
            accept_multiple_files=True,
            help=texts["FILE_UPLOADER_HELP"]
        )

        if uploaded_files and st.session_state.rag_system:
            for uploaded_file in uploaded_files:
                add_button_label = f"{texts['ADD_FILE_BUTTON_LABEL']} {uploaded_file.name}"
                
                if st.button(add_button_label, key=f"add_{uploaded_file.name}"):
                    with st.spinner(f"{texts['PROCESSING_FILE']} {uploaded_file.name}..."):
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
                                content = uploaded_file.getvalue().decode("utf-8")
                                st.session_state.rag_system.add_text_document(
                                    content,
                                    uploaded_file.name.split('.')[0],
                                    {"source": uploaded_file.name, "type": "uploaded"}
                                )
                                result = f"{texts['FILE_ADD_SUCCESS']} {uploaded_file.name}"
                            
                            st.success(result)
                        except Exception as e:
                            st.error(f"{texts['FILE_ERROR']} {uploaded_file.name}: {str(e)}")
                        finally:
                            os.unlink(tmp_path)

                        st.rerun()

        # Add text document
        with st.expander(texts["ADD_TEXT_EXPANDER"]):
            doc_title = st.text_input(texts["DOC_TITLE_INPUT"])
            doc_content = st.text_area(texts["DOC_CONTENT_INPUT"], height=200)

            if st.button(texts["ADD_DOC_BUTTON"]) and doc_title and doc_content and st.session_state.rag_system:
                st.session_state.rag_system.add_text_document(
                    doc_content,
                    doc_title.lower().replace(" ", "_"),
                    {"title": doc_title, "type": "manual_entry"}
                )
                st.success(f"{texts['ADD_DOC_SUCCESS']} {doc_title}")
                st.rerun()

        # Load sample documents
        if st.button(texts["LOAD_SAMPLE_BUTTON"]) and st.session_state.rag_system:
            result = load_sample_documents(st.session_state.rag_system)
            st.success(result)
            st.rerun()

        st.divider()

        # Quick actions
        if st.button(texts["CLEAR_CHAT_BUTTON"]):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # Stats
        if st.session_state.rag_system:
            stats = st.session_state.rag_system.get_stats()
            st.markdown(f"### {texts['STATS_HEADER']}")
            st.metric(texts["STATS_DOCUMENTS"], stats.get("total_documents", 0))
            st.metric(texts["STATS_CHUNKS"], stats.get("total_chunks", 0))

        # Search API status
        st.divider()
        st.markdown(f"### {texts['SEARCH_API_HEADER']}")
        serper_key = os.getenv("SERPER_API_KEY")
        st.write(f"**Serper** {'✅' if serper_key else '❌'}")
        
        st.divider()
        st.markdown(f"### {texts['ABOUT_HEADER']}")
        st.markdown(texts["ABOUT_FEATURES_HEADER"])
        st.markdown(texts["ABOUT_FEATURES"])
        st.markdown(texts["ABOUT_STUDENTS_HEADER"])
        st.markdown(texts["ABOUT_STUDENTS"])
        st.markdown(texts["ABOUT_SEARCH_HEADER"])
        st.markdown(texts["ABOUT_SEARCH_TEXT"])

    # Main interface - Two tabs
    tab1, tab2 = st.tabs([texts["TAB_CHAT"], texts["TAB_DOCUMENTS"]])

    with tab1:
        # Main chat interface
        if not st.session_state.llm_client or not st.session_state.rag_system:
            st.markdown(f"""
                <div class="info-card">
                    <h2>{texts['WELCOME_TITLE']}</h2>
                    <p>
                        {texts['WELCOME_MESSAGE']}
                    </p>
                    {texts['WELCOME_FEATURES_LIST']}
                </div>
            """, unsafe_allow_html=True)
            st.warning(texts["WELCOME_WARNING"])
            return

        # Display existing chat messages
        display_chat_messages(texts)

        # Example queries
        st.markdown(f"### {texts['EX_QUERY_HEADER']}")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(texts["EX_QUERY_1"]):
                st.session_state.example_query = texts["EX_QUERY_1"]

        with col2:
            if st.button(texts["EX_QUERY_2"]):
                st.session_state.example_query = texts["EX_QUERY_2"]

        with col3:
            if st.button(texts["EX_QUERY_3"]):
                st.session_state.example_query = texts["EX_QUERY_3"]

        # Chat input
        prompt = st.chat_input(texts["CHAT_INPUT_PLACEHOLDER"])

        # Handle example query
        if hasattr(st.session_state, 'example_query'):
            prompt = st.session_state.example_query
            delattr(st.session_state, 'example_query')

        if prompt:

            # Display user message
            # Add user message to chat history
            with st.chat_message(texts["USER_ROLE"]):
                st.markdown(prompt)
                st.session_state.messages.append({"role": texts["USER_ROLE"], "content": prompt})
            
            # Check if the query is sleep related
            if not is_sleep_related_query(prompt):
                with st.chat_message(texts["ASSISTANT_ROLE"]):
                    sorry_msg = texts["NON_SLEEP_WARNING"]
                    st.markdown(sorry_msg)
                    st.session_state.messages.append({
                        "role": texts["ASSISTANT_ROLE"],
                        "content": sorry_msg,
                        "context_used": False,
                        "search_used": False
                    })
            
            if is_sleep_related_query(prompt):    

                # Generate and display assistant response
                with st.chat_message(texts["ASSISTANT_ROLE"]):
                    with st.spinner(texts["ASSISTANT_SPINNER"]):
                        
                        # Get relevant context from RAG system
                        context = st.session_state.rag_system.get_context_for_query(
                            prompt, max_context_length=context_max_tokens)

                        search_used = False
                        search_context = ""

                        # --- First, try to answer with RAG (RAG-Only Prompt) ---
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

                        # --- Check for INSUFFICIENT_CONTEXT and fallback to Web Search (NEW) ---
                        if "INSUFFICIENT_CONTEXT" in initial_response and enable_web_search:
                            st.warning(texts["RAG_NOT_ENOUGH_WARNING"])
                            st.info(texts["SEARCHING_WEB_INFO"])

                            # Execute Search
                            # The prompt for the search engine itself should still be clear
                            enhanced_prompt_search = prompt + " ONLY SEARCH FROM WEBSITE THAT HAVE RESEARCH-BACKED RESOURCES ABOUT SLEEPING "
                            search_results = execute_search(enhanced_prompt_search, web_search_results)
                            search_context = search_results
                            search_used = True

                            st.success(f"✅ {texts['WEB_SEARCH_SUCCESS']} {web_search_results} {texts['WEB_SOURCES_LABEL']}.")
                            
                            # Web Search Prompt (with full core instructions)
                            enhanced_prompt = f"""
                            You are a highly specialized sleep expert with an exceptional ability to simplify complex topics.

                            Core Instructions:
                            1. Level of Detail & Simplicity: Your answers must be detailed and comprehensive, treating the user as a complete novice. Use simple, clear language and fully explain all core concepts.
                            2. **Language Match: Answer in the same language used by the user (Thai or English). Ensure natural and fluent language.**
                            3. Content Scope: Focus exclusively on sleep-related topics.
                            4. Web Search Context: Below is current information from the web. Use this to answer comprehensively.

                            [Web Search Results]
                            {search_context}

                            User Question: {prompt}

                            Please provide a comprehensive answer based on the web search results above. Synthesize information from multiple sources and present it clearly.
                            """
                            
                            # Get new response with web search context
                            message_web = []
                            for msg in st.session_state.messages[:-1]:
                                message_web.append({"role": msg["role"], "content": msg["content"]})
                            message_web.append({"role": "user", "content": enhanced_prompt})

                            response = st.session_state.llm_client.chat(message_web)
                            
                        elif "INSUFFICIENT_CONTEXT" in initial_response and not enable_web_search:
                            st.warning(texts["RAG_NOT_ENOUGH_WARNING"])
                            st.warning(texts["WEB_DISABLED_WARNING"])
                            response = texts["RAG_NO_ANSWER"]
                        
                        else:
                            # RAG is good, use the initial response
                            response = initial_response
                            search_context = context # Use RAG context for display
                            
                        # Display response
                        st.markdown(response)

                        # Show retrieved context in expander
                        if search_used:
                            with st.expander(texts["WEB_RESULTS_EXPANDER"]):
                                st.markdown(search_context)
                        else:
                            with st.expander(texts["RETRIEVED_CONTEXT_EXPANDER"]):
                                st.markdown(context)

                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": texts["ASSISTANT_ROLE"],
                            "content": response,
                            "context_used": True,
                            "search_used": search_used
                        })

    with tab2:
        # Document management tab
        display_documents(texts)


if __name__ == "__main__":
    main()