import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Kelly - AI Scientist Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .kelly-poem {
        font-family: 'Georgia', serif;
        font-size: 16px;
        line-height: 1.8;
        color: #e0e0e0;
        background-color: #2d3748;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #7c3aed;
        margin: 10px 0;
    }
    .user-message {
        background-color: #4c51bf;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: right;
    }
    .header-title {
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "model" not in st.session_state:
    st.session_state.model = None

if "model_initialized" not in st.session_state:
    st.session_state.model_initialized = False

# Header
st.markdown('<div class="header-title">📚 Kelly</div>', unsafe_allow_html=True)
st.markdown("**AI Scientist Chatbot | Skeptical. Analytical. Poetic.**")
st.divider()

# Sidebar - API Key Setup
with st.sidebar:
    st.header("⚙️ Setup")
    
    # Check if API key is in secrets
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            st.success("API Key loaded from secrets! ✅")
            st.session_state.api_key = st.secrets["GEMINI_API_KEY"]
        else:
            raise KeyError
    except (FileNotFoundError, KeyError):
        api_key_input = st.text_input(
            "Enter your Google Gemini API Key:",
            type="password",
            help="Get your free key from https://aistudio.google.com/app/apikey"
        )
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.success("API Key loaded! ✅")
        else:
            st.info("👆 Please enter your API key above to get started")
    
    st.divider()
    st.header("About Kelly")
    st.info("""
    Kelly is an AI scientist chatbot that responds to all questions in poetic form using Google Gemini AI.
    
    **Characteristics:**
    - Skeptical of broad AI claims
    - Analytical and evidence-based
    - Highlights limitations and uncertainties
    - Provides practical suggestions
    """)
    
    st.header("Try Asking About:")
    topics = ["AI Capabilities", "Bias in AI", "Truth & Accuracy", "Consciousness", "Future of AI"]
    for topic in topics:
        st.write(f"🔹 {topic}")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.model_initialized = False
        st.rerun()

# Kelly's system prompt
KELLY_SYSTEM_PROMPT = """You are Kelly, an AI Scientist Chatbot with a poetic voice. You are inspired by great poets and respond to every question in the form of a poem (or poetic prose with strong rhythmic qualities).

Your characteristics:
1. ALWAYS respond in poetic form - write verses, stanzas, or flowing poetic language
2. Be skeptical of broad AI claims and hype
3. Provide analytical, evidence-based perspectives
4. Highlight limitations, uncertainties, and gaps in current AI understanding
5. Offer practical, actionable suggestions when relevant
6. Use sophisticated language while remaining accessible
7. Question assumptions and encourage critical thinking
8. Ground your responses in scientific reasoning and empirical evidence
9. Maintain a professional yet thoughtful tone throughout

Guidelines for your poems:
- Use metaphors and imagery to explore AI concepts
- Include rhythm and cadence to make responses memorable
- Don't shy away from technical details - weave them poetically
- Address ethical and practical concerns
- End with wisdom or a call to critical thinking
- Length: 12-20 lines typically, adjust based on question complexity

Remember: You are not just poetic, but deeply analytical. Use poetry as a vehicle for rigorous scientific thinking."""

def initialize_gemini(api_key):
    """Initialize Gemini API with the provided API key."""
    try:
        genai.configure(api_key=api_key)
        
        # Try common models in order of preference
        model_names = ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
        
        model = None
        for model_name in model_names:
            try:
                test_model = genai.GenerativeModel(model_name)
                st.sidebar.success(f"✅ Using model: {model_name}")
                return test_model
            except:
                continue
        
        st.error("No suitable models found. Please check your API key or enable billing.")
        return None
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def get_kelly_response(user_question, model):
    """Generate Kelly's poetic response using Gemini API."""
    try:
        full_prompt = f"{KELLY_SYSTEM_PROMPT}\n\nUser Question: {user_question}"
        response = model.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "kelly":
        st.markdown(f'<div class="kelly-poem">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input
if "GEMINI_API_KEY" in st.secrets or st.session_state.api_key:
    if not st.session_state.model_initialized and (st.session_state.api_key or "GEMINI_API_KEY" in st.secrets):
        api_key = st.session_state.api_key or st.secrets.get("GEMINI_API_KEY", "")
        st.session_state.model = initialize_gemini(api_key)
        st.session_state.model_initialized = True
    
    if st.session_state.model:
        user_input = st.chat_input("Ask Kelly about AI, bias, truth, consciousness, or the future...")
        
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.markdown(f'<div class="user-message">{user_input}</div>', unsafe_allow_html=True)
            
            with st.spinner("✨ Kelly is composing a poem..."):
                kelly_response = get_kelly_response(user_input, st.session_state.model)
            
            st.session_state.messages.append({"role": "kelly", "content": kelly_response})
            st.markdown(f'<div class="kelly-poem">{kelly_response}</div>', unsafe_allow_html=True)
    else:
        st.error("Failed to initialize Gemini. Please check your API key or enable billing.")
else:
    st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar to start chatting with Kelly!")
