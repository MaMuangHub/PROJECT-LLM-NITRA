"""
Chat Application with Web Search Tool Calling - FIXED VERSION
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# โหลด .env อย่างชัดเจน
load_dotenv(override=True)

serper = os.getenv("SERPER_API_KEY")
tavily = os.getenv("TAVILY_API_KEY")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.llm_client import LLMClient, get_available_models
from utils.search_tools import WebSearchTool, format_search_results

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = None
    if "search_tool" not in st.session_state:
        st.session_state.search_tool = WebSearchTool()

def execute_search(query: str, num_results: int = 5):
    """Execute web search and return formatted results"""
    print(f"\n{'='*60}")
    print(f"🔍 execute_search() called with query: '{query}'")
    print(f"{'='*60}")
    
    # ใช้ search_tool ไม่ใช่ conversion_tools
    results = st.session_state.search_tool.search(query, num_results)
    
    print(f"📊 Results received: {len(results)} items")
    if results and "error" in str(results[0]):
        print(f"❌ Error in results: {results}")
    else:
        print(f"✅ Search successful!")
    
    formatted = format_search_results(results)
    print(f"📝 Formatted output length: {len(formatted)} chars\n")
    
    return formatted

def handle_tool_calls(message_content: str):
    """Handle potential tool calls in the message"""
    message_lower = message_content.lower()

    search_triggers = [
        "search:", "search for", "look up", "find information", "google",
        "current", "latest", "recent", "today", "now", "this week", "2024", "2025",
        "news", "update", "happened", "breaking", "announcement",
        "stock", "price", "weather", "temperature", "forecast",
        "game", "match", "score", "won", "championship", "tournament",
        "trending", "viral", "popular",
        "what's new", "what happened", "any updates",
        "convert", "conversion", "exchange rate", "currency",
        "USD", "EUR", "GBP", "JPY", "CNY", "BTC", "ETH",
    ]

    should_search = any(trigger in message_lower for trigger in search_triggers)

    time_words = ["today", "now", "current", "latest", "recent", "2024", "2025"]
    question_words = ["what", "how", "when", "where", "who", "why"]

    has_time_word = any(word in message_lower for word in time_words)
    has_question_word = any(word in message_lower for word in question_words)

    if has_time_word and has_question_word:
        should_search = True

    if should_search:
        query = message_content
        
        prefixes_to_remove = [
            "search:", "search for", "look up", "find information about",
            "tell me about", "what is", "what are", "how is"
        ]

        for prefix in prefixes_to_remove:
            if message_lower.startswith(prefix):
                query = query[len(prefix):].strip()
                break

        if query.endswith("?"):
            query = query[:-1].strip()
        if not query:
            query = message_content

        print(f"\n🎯 Search triggered! Query: '{query}'")
        search_results = execute_search(query, 5)

        # ตรวจสอบว่าการค้นหาสำเร็จหรือไม่
        if "Error:" in search_results or "No search results" in search_results:
            st.error(f"⚠️ การค้นหาล้มเหลว!\n\n{search_results}")
            return message_content, False

        enhanced_prompt = f"""
        User Query: {message_content}

        I have searched the web and found the following current information:

        {search_results}

        Please provide a comprehensive answer based on this information.
            """
        return enhanced_prompt, True

    return message_content, False

def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("search_used", False):
                st.markdown("🔍 *Used web search*")
            st.markdown(message["content"])

def main():
    st.set_page_config(
        page_title="Chat with Web Search",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Chat with Web Search")
    st.markdown("AI chat with **automatic** web search - FIXED VERSION")

    init_session_state()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        available_models = get_available_models()
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=0
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1
        )

        max_tokens = st.slider(
            "Max Tokens",
            min_value=50,
            max_value=4000,
            value=2000,
            step=50
        )

        if st.button("Initialize Model") or st.session_state.llm_client is None:
            with st.spinner("Initializing model..."):
                st.session_state.llm_client = LLMClient(
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            st.success(f"Model {selected_model} initialized!")

        st.divider()

        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()

        st.subheader("🔧 API Status")
        serper_key = os.getenv("SERPER_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")

        st.write(f"**Serper API:** {'✅ Configured' if serper_key else '❌ Not configured'}")
        st.write(f"**Tavily API:** {'✅ Configured' if tavily_key else '❌ Not configured'}")

        if serper_key:
            st.code(f"Key: {serper_key[:10]}...{serper_key[-5:]}")
        
        if not serper_key and not tavily_key:
            st.error("⚠️ No search APIs configured!")
            st.info("Add to .env file:\nSERPER_API_KEY=your_key\nor\nTAVILY_API_KEY=your_key")

    if not st.session_state.llm_client:
        st.warning("⚠️ Please initialize a model in the sidebar first!")
        return

    display_chat_messages()

    st.markdown("### 💡 Try these:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🌤️ Weather in Tokyo"):
            st.session_state.example_query = "What's the weather in Tokyo today?"

    with col2:
        if st.button("📈 AI News 2025"):
            st.session_state.example_query = "Latest AI developments in 2025"

    with col3:
        if st.button("💼 Stock Market"):
            st.session_state.example_query = "How is the stock market today?"

    prompt = st.chat_input("Ask anything...")

    if hasattr(st.session_state, 'example_query'):
        prompt = st.session_state.example_query
        delattr(st.session_state, 'example_query')

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                enhanced_prompt, search_used = handle_tool_calls(prompt)

                if search_used:
                    st.markdown("🔍 *Searching the web...*")

                messages = []
                for msg in st.session_state.messages[:-1]:
                    messages.append({"role": msg["role"], "content": msg["content"]})

                messages.append({"role": "user", "content": enhanced_prompt})

                response = st.session_state.llm_client.chat(messages)
                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "search_used": search_used
                })

if __name__ == "__main__":
    main()
