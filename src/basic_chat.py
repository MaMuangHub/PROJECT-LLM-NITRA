"""
Basic Chat Application with LiteLLM
A simple chat interface demonstrating LLM integration with Streamlit
"""


import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from utils.llm_client import LLMClient, get_available_models #backend is here import from client

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = None 


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    st.set_page_config(
        page_title="Basic Chat App",
        page_icon="💬",
        layout="wide"
    )

    st.title("💬 Basic Chat Application")
    st.markdown(
        "A simple chat interface using LiteLLM - Perfect starter code for LLM projects!")

    # Initialize session state
    init_session_state()

    # Sidebar configuration
    with st.sidebar: #side bar 
        st.header("⚙️ Configuration")

        # Model selection
        available_models = get_available_models()
        selected_model = st.selectbox(
            "Select Model",
            available_models, #import form client 
            index=0,
            help="Choose the language model to use"
        )

        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in responses"
        )

        # Max tokens
        max_tokens = st.slider(
            "Max Tokens",
            min_value=50,
            max_value=4000,
            value=1000,
            step=50,
            help="Maximum length of response"
        )

        # Initialize LLM client
        if st.button("Initialize Model") or st.session_state.llm_client is None:
            with st.spinner("Initializing model..."):#set state
                st.session_state.llm_client = LLMClient( #create model LLMClient
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            st.success(f"Model {selected_model} initialized!")

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
 

        # Model info
        st.subheader("📊 Model Info")
        if st.session_state.llm_client:# display MODEL INFO
            st.write(f"**Model:** {st.session_state.llm_client.model}")
            st.write(
                f"**Temperature:** {st.session_state.llm_client.temperature}")
            st.write(
                f"**Max Tokens:** {st.session_state.llm_client.max_tokens}")

        st.divider()
        st.markdown("### 📚 About")
        st.markdown("""
        This basic chat app demonstrates:
        - LiteLLM integration
        - Streamlit chat interface
        - Session state management
        - Model configuration
        
        **For Students:**
        - Modify the prompt handling
        - Add system messages
        - Implement chat history persistence
        - Add response streaming
        """)

    # Main chat interface
    if not st.session_state.llm_client:
        st.warning("⚠️ Please initialize a model in the sidebar first!")
        return

    # Display existing chat messages
    display_chat_messages()
    
    
    

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        user_time = datetime.now().strftime("%H:%M.%S")

        st.session_state.messages.append({"role": "user", "content": prompt})


        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.markdown(user_time)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Prepare messages for LLM
                messages = [{"role": msg["role"], "content": msg["content"]}
                            for msg in st.session_state.messages]

                # Get response from LLM
                response = st.session_state.llm_client.chat(messages)
                
                assistant_time = datetime.now().strftime("%H:%M.%S")

                # Display response
                st.markdown(response)

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response})
                st.markdown(assistant_time)


if __name__ == "__main__":
    main()
