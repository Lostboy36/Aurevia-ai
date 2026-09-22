import streamlit as st
from google import genai
import pypdf

# 1. Page Configuration
st.set_page_config(
    page_title="Aurevia AI",
    page_icon="✨",
    layout="centered"
)

# 2. Custom "Warm Horizon" Theme (Claude-Inspired CSS)
custom_css = """
<style>
    /* Main app background & base font */
    .stApp {
        background-color: #FBF9F5;
        color: #2D2825;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F3EFE8;
        border-right: 1px solid #E5DFD5;
    }
    
    /* Header styling */
    .aurevia-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #EBE5DC;
    }
    .aurevia-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #C85A32;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .aurevia-subtitle {
        font-size: 0.95rem;
        color: #706860;
        margin-top: 0.3rem;
    }

    /* Message Cards */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 1rem !important;
    }

    /* User Message (Warm Sand) */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #F2E8DC !important;
        border: 1px solid #E6D8C6 !important;
        color: #2D2825 !important;
    }

    /* Assistant Message (Warm White) */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #FFFFFF !important;
        border: 1px solid #EBE5DC !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        color: #2D2825 !important;
    }

    /* Input Box */
    .stChatInputContainer textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #DCD5CA !important;
        border-radius: 10px !important;
        color: #2D2825 !important;
    }
    .stChatInputContainer textarea:focus {
        border-color: #C85A32 !important;
        box-shadow: 0 0 0 2px rgba(200, 90, 50, 0.15) !important;
    }

    /* Clean up Streamlit default menu/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Header
st.markdown("""
<div class="aurevia-header">
    <div class="aurevia-title">✨ Aurevia AI</div>
    <div class="aurevia-subtitle">Your thoughtful, intelligent conversational partner</div>
</div>
""", unsafe_allow_html=True)

# 4. Sidebar Controls, Document Upload (RAG) & About Section
doc_text = ""

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key:", type="password", help="Enter your free API key from Google AI Studio")
    st.markdown("[Get a free Gemini API Key](https://aistudio.google.com/)")
    
    st.divider()
    st.header("📄 Knowledge Base (RAG)")
    uploaded_file = st.file_uploader("Upload a PDF or TXT document:", type=["pdf", "txt"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(uploaded_file)
                extracted_pages = [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
                doc_text = "\n".join(extracted_pages)
                st.success(f"Loaded '{uploaded_file.name}' ({len(pdf_reader.pages)} pages)")
            elif uploaded_file.name.endswith(".txt"):
                doc_text = uploaded_file.read().decode("utf-8")
                st.success(f"Loaded '{uploaded_file.name}'")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.divider()
    st.header("ℹ️ About")
    st.markdown(
        "**Aurevia AI** is an intelligent, document-aware conversational assistant.\n\n"
        "✨ **Developed by Lostboy**"
    )

    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.selected_starter = None
        st.rerun()

# 5. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_starter" not in st.session_state:
    st.session_state.selected_starter = None

# 6. Prompt Starter Buttons (Shown when chat is empty)
if not st.session_state.messages:
    st.markdown("##### 💡 Need inspiration? Try a prompt starter:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💡 Brainstorm project ideas", use_container_width=True):
            st.session_state.selected_starter = "Can you help me brainstorm 5 unique ideas for a creative project?"
        if st.button("🐍 Write & explain code", use_container_width=True):
            st.session_state.selected_starter = "Write a simple Python script for data analysis and explain how it works."
            
    with col2:
        if st.button("📄 Summarize document", use_container_width=True):
            if uploaded_file:
                st.session_state.selected_starter = "Please summarize the main key points from the uploaded document."
            else:
                st.session_state.selected_starter = "What are the best techniques for summarizing long reports effectively?"
        if st.button("✍️ Draft a professional email", use_container_width=True):
            st.session_state.selected_starter = "Draft a polite and professional follow-up email after a job interview."

# 7. Display Conversation History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. User Chat Input & Trigger Logic
chat_input_val = st.chat_input("Message Aurevia...")

prompt_to_process = None
if st.session_state.selected_starter:
    prompt_to_process = st.session_state.selected_starter
    st.session_state.selected_starter = None
elif chat_input_val:
    prompt_to_process = chat_input_val

# 9. Handle Response Generation
if prompt_to_process:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar settings to begin.")
    else:
        # Display user input
        st.chat_message("user").markdown(prompt_to_process)
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})

        # System instructions with RAG context
        system_instruction = (
            "You are Aurevia, a friendly, eloquent, highly intelligent, and helpful "
            "conversational AI assistant created by Lostboy. Maintain a warm, clear, and thoughtful tone."
        )
        
        if doc_text:
            system_instruction += (
                "\n\n--- UPLOADED KNOWLEDGE BASE DOCUMENT ---\n"
                f"{doc_text}\n"
                "--- END OF DOCUMENT ---\n"
                "When responding to queries related to the document, use the provided document context above to accurately ground your answers."
            )

        # Connect to Gemini API
        client = genai.Client(api_key=api_key)
        
        with st.chat_message("assistant"):
            with st.spinner("Aurevia is thinking..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_to_process,
                        config={'system_instruction': system_instruction}
                    )
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as err:
                    st.error(f"API Error: {err}")
