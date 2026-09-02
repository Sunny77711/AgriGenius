import os
import re
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv("keys.env")

from google import genai
from google.genai import types

from rag_pipeline import (
    AgriGeniusRAG,
    RetrievedSource,
    infer_crop_filter,
    infer_query_type_filter,
    DEFAULT_FETCH_K,
    DEFAULT_TOP_K,
    LLM_MODEL_NAME,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="AgriGenius — AI Farming Advisory",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Premium CSS Styling ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hero Banner */
.hero-container {
    background: linear-gradient(135deg, #064E3B 0%, #047857 50%, #059669 100%);
    color: white;
    padding: 2.2rem 2.5rem;
    border-radius: 20px;
    margin-bottom: 1.8rem;
    box-shadow: 0 10px 30px rgba(4, 120, 87, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.15);
    position: relative;
    overflow: hidden;
}
.hero-container::after {
    content: "🌾";
    font-size: 8rem;
    position: absolute;
    right: 20px;
    bottom: -20px;
    opacity: 0.12;
    pointer-events: none;
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #D1FAE5;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    max-width: 780px;
    line-height: 1.5;
}
.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}
.hero-badge {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #ECFDF5;
}

/* Section Headings */
.section-heading {
    font-size: 1.15rem;
    font-weight: 700;
    color: #065F46;
    margin: 1.4rem 0 0.6rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Detected Labels Bar */
.detected-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    padding: 0.85rem 1.2rem;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 12px;
    margin-bottom: 1.2rem;
    align-items: center;
}
.detected-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.75rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
}
.pill-crop {
    background: #DCFCE7;
    color: #166534;
    border: 1px solid #86EFAC;
}
.pill-category {
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
}
.pill-lang {
    background: #E0E7FF;
    color: #3730A3;
    border: 1px solid #C7D2FE;
}
.pill-mode {
    background: #F3E8FF;
    color: #6B21A8;
    border: 1px solid #E9D5FF;
}

/* Source Evidence Card */
.source-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.03);
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.source-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.07);
    border-color: #10B981;
}
.source-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.6rem;
    gap: 0.5rem;
}
.source-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.source-pill {
    font-size: 0.76rem;
    font-weight: 600;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    background: #F1F5F9;
    color: #334155;
}
.sim-score-high {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    background: #DCFCE7;
    color: #166534;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    border: 1px solid #86EFAC;
    white-space: nowrap;
}
.sim-score-med {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    background: #FEF3C7;
    color: #92400E;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    border: 1px solid #FDE68A;
    white-space: nowrap;
}
.source-text {
    font-size: 0.95rem;
    color: #1E293B;
    line-height: 1.6;
    background: #F8FAFC;
    padding: 0.85rem 1rem;
    border-left: 3px solid #10B981;
    border-radius: 6px;
    margin-top: 0.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Resource Caching for AgriGenius RAG Pipeline ---
@st.cache_resource(show_spinner=False)
def get_rag_pipeline() -> AgriGeniusRAG:
    """Load and cache the AgriGenius RAG pipeline (embedder + ChromaDB)."""
    return AgriGeniusRAG()


# --- Helper Functions ---
def detect_language(text: str) -> str:
    """Detect if query is primarily Hindi or English."""
    if re.search(r"[\u0900-\u097F]", text):
        return "Hindi (हिन्दी)"
    return "English"


def transcribe_audio(audio_bytes: bytes, api_key: str) -> str:
    """Transcribe farmer's voice query using Gemini."""
    client = genai.Client(api_key=api_key)
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
    prompt = "Transcribe this agricultural query accurately in the exact language spoken (Hindi or English). Return ONLY the transcription text."
    response = client.models.generate_content(
        model=LLM_MODEL_NAME, contents=[audio_part, prompt]
    )
    return (response.text or "").strip()


def calculate_grounding(sources: list[RetrievedSource]) -> tuple[float, str, str]:
    """Calculate grounding confidence score and badge label."""
    if not sources:
        return 0.0, "low", "No Grounding Evidence"

    similarities = [s.similarity for s in sources]
    avg_sim = sum(similarities) / len(similarities)
    max_sim = max(similarities)

    # Weighted grounding metric (65% peak match, 35% breadth)
    grounding_score = (0.65 * max_sim + 0.35 * avg_sim) * 100
    grounding_score = max(0.0, min(100.0, grounding_score))

    if max_sim >= 0.75:
        return grounding_score, "high", "High Grounding (Strong KCC Evidence)"
    elif max_sim >= 0.60:
        return grounding_score, "med", "Moderate Grounding (Topical Match)"
    else:
        return grounding_score, "low", "Low / General Grounding"


# --- Session State Initialization ---
if "submitted_query" not in st.session_state:
    st.session_state.submitted_query = ""
if "last_processed_query" not in st.session_state:
    st.session_state.last_processed_query = None
if "result_data" not in st.session_state:
    st.session_state.result_data = None
if "history" not in st.session_state:
    st.session_state.history = []

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Pipeline Settings")

    with st.container(border=True):
        st.markdown("**🔑 Gemini API Credentials**")
        env_key = os.environ.get("GEMINI_API_KEY", "")
        api_key_input = st.text_input(
            "Gemini API Key",
            value="",
            type="password",
            placeholder="Leave blank to use .env key",
            help="Your key is kept locally in this session.",
        )
        active_api_key = api_key_input.strip() if api_key_input.strip() else env_key

        if active_api_key:
            st.success("API Key Active", icon=":material/key:")
        else:
            st.warning("No API Key detected! Add to .env or paste above.")

    with st.container(border=True):
        st.markdown("**🔍 Retrieval Parameters**")
        top_k = st.slider("Passages to LLM (Top-K)", min_value=1, max_value=10, value=DEFAULT_TOP_K)
        fetch_k = st.slider(
            "Candidate Pool (Fetch-K)", min_value=10, max_value=50, value=DEFAULT_FETCH_K
        )
        use_mmr = st.toggle("MMR Diversification", value=True, help="Prevents repetitive near-duplicate advice")
        auto_filter = st.toggle(
            "Auto Metadata Filter", value=True, help="Auto-detects crops & categories for precision retrieval"
        )

    with st.container(border=True):
        st.markdown("**📊 Knowledge Base Status**")
        with st.spinner("Connecting to ChromaDB..."):
            try:
                rag = get_rag_pipeline()
                count = rag.collection_count()
                st.success(f"**{count:,}** KCC advisory vectors online", icon=":material/check_circle:")
            except Exception as e:
                st.error(f"Error loading vector index: {e}")
                st.stop()

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.result_data = None
        st.session_state.history = []
        st.session_state.submitted_query = ""
        st.session_state.last_processed_query = None
        st.rerun()

# --- Main Page Layout ---

# 1. Hero Banner
st.markdown(
    f"""
<div class="hero-container">
    <h1 class="hero-title">🌾 AgriGenius</h1>
    <div class="hero-subtitle">
        Bilingual English-Hindi smart farming assistant grounded in verified Kisan Call Centre (KCC) expert advisories.
    </div>
    <div class="hero-badges">
        <span class="hero-badge">📦 347,944 Advisory Records</span>
        <span class="hero-badge">🧠 l3cube-pune/hindi-sentence-bert-nli</span>
        <span class="hero-badge">⚡ {LLM_MODEL_NAME}</span>
        <span class="hero-badge">🛡️ MMR Diversified</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# 2. Demo Query Buttons Section
st.markdown('<div class="section-heading">💡 Quick Demo Queries (Click to Run)</div>', unsafe_allow_html=True)

demo_cols_row1 = st.columns(3)
demo_cols_row2 = st.columns(3)

demo_cases = [
    ("🌾 Wheat Irrigation", "गेहूं की फसल में सिंचाई कब करनी चाहिए?"),
    ("🌿 Paddy Weed Control", "धान की फसल में खरपतवार को कैसे नियंत्रित करें?"),
    ("🥭 Mango Pest Care", "How do I control pests in mango trees?"),
    ("🎋 Sugarcane Fertilizer", "What fertilizer should I use for sugarcane?"),
    ("🥜 Groundnut Seed Rate", "मूंगफली की फसल में बीज दर क्या है?"),
    ("🧅 Onion Weed Care", "How to manage weeds in onion crop?"),
]

for idx, (label, query_text) in enumerate(demo_cases):
    col = demo_cols_row1[idx] if idx < 3 else demo_cols_row2[idx - 3]
    with col:
        if st.button(label, key=f"demo_btn_{idx}", use_container_width=True):
            st.session_state.submitted_query = query_text

# 3. Query Area Section
st.markdown('<div class="section-heading">🔎 Ask Your Farming Question</div>', unsafe_allow_html=True)

with st.container(border=True):
    col_input, col_submit = st.columns([5, 1])

    with col_input:
        user_text = st.text_input(
            "Enter agricultural question:",
            value=st.session_state.submitted_query,
            placeholder="e.g., What is the seed rate for groundnut? or गेहूं में पहली सिंचाई कब करें?",
            label_visibility="collapsed",
            key="text_query_field",
        )

    with col_submit:
        submit_clicked = st.button("Ask Advisor 🚜", type="primary", use_container_width=True)

    # Optional Voice Query
    with st.expander("🎙️ Speak Your Query (Voice Input)", expanded=False):
        voice_audio = st.audio_input("Record farming question", label_visibility="collapsed")
        if voice_audio is not None and active_api_key:
            if st.button("Transcribe & Ask Voice Query", type="secondary"):
                with st.spinner("Transcribing audio via Gemini..."):
                    try:
                        audio_bytes = voice_audio.read()
                        transcribed = transcribe_audio(audio_bytes, active_api_key)
                        if transcribed:
                            st.session_state.submitted_query = transcribed
                            st.rerun()
                        else:
                            st.warning("Could not transcribe any audio.")
                    except Exception as ex:
                        st.error(f"Transcription error: {ex}")

# Check trigger
active_query = None
if submit_clicked and user_text.strip():
    active_query = user_text.strip()
elif st.session_state.submitted_query and st.session_state.submitted_query != st.session_state.last_processed_query:
    active_query = st.session_state.submitted_query.strip()

# --- Process RAG Query when triggered ---
if active_query:
    if not active_api_key:
        st.error("⚠️ Gemini API Key is missing. Please enter it in the sidebar or provide it in keys.env / .env")
        st.stop()

    st.session_state.last_processed_query = active_query

    # Query Intent Detection
    crop_filter = infer_crop_filter(active_query)
    query_type_filter = infer_query_type_filter(active_query)
    detected_crop = crop_filter["Crop"] if crop_filter else "Broad Agricultural"
    detected_cat = query_type_filter["QueryType"] if query_type_filter else "General Advisory"
    detected_lang = detect_language(active_query)

    with st.status("🌾 Consulting Kisan Call Centre Records...", expanded=True) as status:
        st.write(f"Analyzing query: *'{active_query}'*")
        st.write(f"Detected Crop: **{detected_crop}** | Category: **{detected_cat}**")
        st.write(f"Searching ChromaDB ({rag.collection_count():,} advisory records)...")

        # 1. Retrieve sources using rag_pipeline
        sources = rag.retrieve_sources(
            query=active_query,
            top_k=top_k,
            fetch_k=fetch_k,
            use_mmr=use_mmr,
            auto_metadata_filter=auto_filter,
        )
        st.write(f"Retrieved **{len(sources)}** diversified source passages.")

        # 2. Generate grounded answer
        st.write(f"Generating grounded answer using {LLM_MODEL_NAME}...")
        try:
            os.environ["GEMINI_API_KEY"] = active_api_key
            answer = rag.generate_answer(active_query, sources)
            status.update(label="✅ Advisory Ready!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="❌ Error generating advisory", state="error", expanded=False)
            st.error(f"Error generating answer: {e}")
            st.stop()

    # Save to session state
    result_entry = {
        "query": active_query,
        "answer": answer,
        "sources": sources,
        "crop": detected_crop,
        "category": detected_cat,
        "language": detected_lang,
    }
    st.session_state.result_data = result_entry
    st.session_state.history.append(result_entry)

# --- Render Results View if Available ---
res = st.session_state.result_data
if res:
    st.markdown("---")

    # 4. Crop/Query-Type Detected Labels Section
    st.markdown(
        f"""
    <div class="detected-bar">
        <span style="font-weight: 700; color: #064E3B; margin-right: 0.5rem;">Detected Context:</span>
        <span class="detected-pill pill-crop">🌾 Crop: {res['crop']}</span>
        <span class="detected-pill pill-category">📋 Category: {res['category']}</span>
        <span class="detected-pill pill-lang">🌐 Language: {res['language']}</span>
        <span class="detected-pill pill-mode">🎯 Mode: {'Targeted Filter' if res['crop'] != 'Broad Agricultural' else 'Semantic Vector Search'}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 5. Answer Card Section
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ECFDF5; padding-bottom: 0.6rem; margin-bottom: 1rem;">
                <div style="font-size: 1.25rem; font-weight: 700; color: #064E3B; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🌱</span> KCC Expert Advisory
                </div>
                <div style="font-size: 0.85rem; color: #059669; font-weight: 700; background: #ECFDF5; padding: 0.25rem 0.75rem; border-radius: 9999px; border: 1px solid #A7F3D0;">
                    Grounded in {len(res['sources'])} Verified Records
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(res["answer"])

    # 6. Confidence / Grounding Indicator Section
    score, badge_level, label = calculate_grounding(res["sources"])
    badge_color = "#15803D" if badge_level == "high" else ("#B45309" if badge_level == "med" else "#B91C1C")
    badge_bg = "#DCFCE7" if badge_level == "high" else ("#FEF3C7" if badge_level == "med" else "#FEE2E2")
    badge_border = "#86EFAC" if badge_level == "high" else ("#FCD34D" if badge_level == "med" else "#FCA5A5")

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="font-weight: 700; font-size: 1.05rem; color: #1F2937; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🛡️</span> Grounding & Evidence Confidence
                </div>
                <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; padding: 0.3rem 0.8rem; border-radius: 9999px; font-weight: 700; font-size: 0.82rem;">
                    {label} ({score:.1f}%)
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(score / 100.0)
        if res["sources"]:
            top_sim = res["sources"][0].similarity
            avg_sim = sum(s.similarity for s in res["sources"]) / len(res["sources"])
            st.markdown(
                f"<div style='font-size: 0.85rem; color: #4B5563; margin-top: 0.4rem;'>"
                f"Peak passage similarity: <b style='color: #065F46;'>{top_sim:.1%}</b> | "
                f"Average corpus relevance: <b style='color: #065F46;'>{avg_sim:.1%}</b> across {len(res['sources'])} diversified advisory passages."
                f"</div>",
                unsafe_allow_html=True,
            )

    # 7. Retrieved Source Cards Section
    st.markdown(
        f'<div class="section-heading">📚 Retrieved Advisory Evidence ({len(res["sources"])} Source Passages)</div>',
        unsafe_allow_html=True,
    )

    if not res["sources"]:
        st.info("No matching source passages found in the KCC database.")
    else:
        for src in res["sources"]:
            crop_meta = src.metadata.get("Crop", "Unspecified Crop")
            district_meta = src.metadata.get("DistrictName", "Unspecified District")
            category_meta = src.metadata.get("QueryType", "General")
            sim_pct = src.similarity * 100
            sim_class = "sim-score-high" if src.similarity >= 0.75 else "sim-score-med"

            st.markdown(
                f"""
            <div class="source-card">
                <div class="source-header">
                    <div class="source-pills">
                        <span class="source-pill" style="background: #065F46; color: #ECFDF5; font-weight: 700;">#{src.rank}</span>
                        <span class="source-pill">🌾 {crop_meta}</span>
                        <span class="source-pill">📍 {district_meta}</span>
                        <span class="source-pill">📋 {category_meta}</span>
                    </div>
                    <span class="{sim_class}">{sim_pct:.1f}% Match</span>
                </div>
                <div class="source-text">
                    "{src.text}"
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# 8. Past Questions History Expander
if len(st.session_state.history) > 1:
    with st.expander(f"📜 Session History ({len(st.session_state.history)} queries)", expanded=False):
        for idx, item in enumerate(reversed(st.session_state.history[:-1]), 1):
            st.markdown(f"**Query {idx}:** {item['query']}")
            st.caption(item["answer"][:180] + ("..." if len(item["answer"]) > 180 else ""))
            st.divider()
