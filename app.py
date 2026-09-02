import streamlit as st
import os
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types

# --- Configuration ---
CHROMA_DB_PATH = "./chroma_kcc_db"
COLLECTION_NAME = "kcc_agri_advisor"
EMBED_MODEL_NAME = "l3cube-pune/hindi-sentence-bert-nli"
LLM_MODEL_NAME = "gemini-3.5-flash"

SYSTEM_INSTRUCTION = """You are a helpful agricultural advisory assistant for farmers in India, \
in the style of Kisan Call Centre expert advice.

Rules:
- Answer ONLY using the information in the provided context passages, which are real \
advisory answers given to other farmers by agricultural experts.
- If the context does not contain enough information to answer confidently, say so \
clearly instead of guessing or inventing details.
- Respond in the SAME language the farmer's question was asked in (Hindi or English).
- Keep the answer practical, specific, and concise -- similar in style and length to \
the source advisory answers, not a long essay.
"""

st.set_page_config(
    page_title="AgriGenius Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Resource Caching ---
@st.cache_resource(show_spinner=False)
def load_retriever():
    model = SentenceTransformer(EMBED_MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    # Use get_or_create to avoid crashing if the user hasn't built the index yet
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return model, collection

# --- Helper Functions ---
def transcribe_audio(audio_bytes, api_key):
    client = genai.Client(api_key=api_key)
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
    transcription_prompt = "Transcribe this agricultural audio query precisely in its original language. Output ONLY the transcription, nothing else."
    response = client.models.generate_content(
        model=LLM_MODEL_NAME,
        contents=[audio_part, transcription_prompt]
    )
    return response.text.strip()

def retrieve(query, model, collection, k=5):
    # Prevent ChromaDB crash if k is larger than the number of vectors in the database
    k = min(k, max(1, collection.count()))
    
    query_embedding = model.encode([query], normalize_embeddings=True)[0]
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    passages = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        similarity = 1 - dist
        passages.append({"text": doc, "metadata": meta, "similarity": similarity})
    return passages

def build_prompt(query, passages):
    context_block = "\n\n".join(
        f"[Passage {i + 1}] (Crop: {p['metadata'].get('Crop', '?')}, "
        f"District: {p['metadata'].get('DistrictName', '?')}, "
        f"Category: {p['metadata'].get('QueryType', '?')})\n{p['text']}"
        for i, p in enumerate(passages)
    )
    return f"Context passages:\n{context_block}\n\nFarmer's question: {query}\n\nAnswer:"

def call_llm(prompt, api_key):
    if not api_key:
        raise ValueError("API Key is missing!")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=LLM_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
        ),
    )
    return response.text

# --- Main App Headers ---
st.title("AgriGenius", icon=":material/eco:")
st.caption("Your Smart Farming Assistant powered by KCC Data")

# --- Next-Level CSS Animations & Glassmorphism ---
st.markdown("""
<style>
/* Smooth fade-in and slide-up for chat messages */
[data-testid="stChatMessage"] {
    animation: slideUpFade 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUpFade {
    0% {
        opacity: 0;
        transform: translateY(20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Glassmorphism for Assistant Bubbles */
[data-testid="chat-message-assistant"] {
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

/* Soft hover effect for Assistant Bubbles */
[data-testid="chat-message-assistant"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

/* Premium Gradient for User Bubbles */
[data-testid="chat-message-user"] {
    background: linear-gradient(135deg, #e6f4ea 0%, #ceead6 100%) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(46, 125, 50, 0.2) !important;
}

/* Dynamic Hover Effects for Sidebar Containers */
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08) !important;
}

/* Glowing Chat Input */
[data-testid="stChatInput"] {
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
[data-testid="stChatInput"]:focus-within {
    box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.3) !important;
    border-color: #2E7D32 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("Settings", icon=":material/settings:")
    
    with st.container(border=True, key="sidebar_container_1"):
        st.subheader("Model Configuration", icon=":material/tune:")
        api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Gemini API Key. Will use environment variable if left blank.")
        top_k = st.slider("Retrieval Passages", min_value=1, max_value=10, value=5)
    
    with st.container(border=True, key="sidebar_container_2"):
        st.subheader("Connection Status", icon=":material/database:")
        with st.spinner("Loading Embedding Model & DB..."):
            try:
                model, collection = load_retriever()
                if collection.count() == 0:
                    st.warning("Database empty! Run index script.", icon=":material/warning:")
                else:
                    st.success(f"Connected ({collection.count():,} vectors)", icon=":material/check_circle:")
            except Exception as e:
                st.error(f"Failed to load DB", icon=":material/error:")
                st.stop()
            
    with st.container(border=True, key="sidebar_container_3"):
        st.subheader("Example Queries", icon=":material/lightbulb:")
        st.markdown("- What is the seed rate for groundnut crop?\n- गेहूं की फसल में सिंचाई कब करनी चाहिए?")

# Determine API Key
api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Namaste! I am AgriGenius. Ask me any agricultural question (in English or Hindi) and I will consult real Kisan Call Centre expert advice to help you."
    })

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = ":material/eco:" if message["role"] == "assistant" else ":material/person:"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Reference Advice", icon=":material/library_books:"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"**Source {idx+1}: {src['metadata'].get('Crop', 'Unknown')} - {src['metadata'].get('DistrictName', 'Unknown')}** (Sim: {src['similarity']:.2f})")
                    st.caption(src["text"])

# React to user input (text or audio)
prompt_input = st.chat_input("Ask your farming question here...", accept_audio=True)

if prompt_input:
    if not api_key:
        st.error("Please enter a Gemini API Key in the sidebar or set GEMINI_API_KEY environment variable.")
        st.stop()
        
    prompt = prompt_input.text
    
    # Process audio if provided
    if prompt_input.audio:
        audio_bytes = prompt_input.audio.read()
        with st.spinner("Transcribing your voice..."):
            try:
                prompt = transcribe_audio(audio_bytes, api_key)
            except Exception as e:
                st.error(f"Failed to transcribe audio: {e}", icon=":material/error:")
                st.stop()

    if prompt:
        # Display user message in chat message container
        st.chat_message("user", avatar=":material/person:").markdown(prompt)
        # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=":material/eco:"):
        
        with st.status("Consulting KCC Records...", expanded=True) as status:
            st.write("Searching database...")
            passages = retrieve(prompt, model, collection, k=top_k)
            st.write(f"Found {len(passages)} relevant expert answers.")
            
            st.write("Generating grounded advice...")
            llm_prompt = build_prompt(prompt, passages)
            
            try:
                answer = call_llm(llm_prompt, api_key)
                status.update(label="Advice ready!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Error generating advice", state="error", expanded=False)
                st.error(f"Error: {e}", icon=":material/error:")
                st.stop()
                
        # Display the answer
        st.markdown(answer)
        
        # Display sources
        with st.expander("View Reference Advice", icon=":material/library_books:"):
             for idx, src in enumerate(passages):
                 st.markdown(f"**Source {idx+1}: {src['metadata'].get('Crop', 'Unknown')} - {src['metadata'].get('DistrictName', 'Unknown')}** (Sim: {src['similarity']:.2f})")
                 st.caption(src["text"])
                 
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": passages
        })
