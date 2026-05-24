import streamlit as st
import os
import uuid
import json
from rag import extract_text, chunk_text, build_index, retrieve, ask_llm

CHAT_FILE = "all_chats.json"

def load_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f, indent=4)

st.set_page_config(page_title="PiscesAI", page_icon="🧠", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=Nunito:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background-color: #f8f5ff;
    color: #2d2250;
}
.stApp {
    background: linear-gradient(135deg, #f0ebff 0%, #e8f4fd 50%, #fef0fb 100%);
    min-height: 100vh;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #2563eb, #0891b2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    text-align: center;
    color: #9ca3af;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 2rem;
    letter-spacing: 0.03em;
}
.user-msg {
    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 14px;
    margin-left: 120px;
    text-align: left;
    box-shadow: 0 4px 18px rgba(124,58,237,0.25);
    font-size: 1rem;
    font-weight: 500;
}
.bot-msg {
    background: #ffffff;
    color: #1e293b;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 18px;
    margin-right: 120px;
    border: 1px solid #ddd6fe;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    font-size: 1rem;
    line-height: 1.7;
}
.user-label {
    text-align: right;
    margin-right: 10px;
    color: #7c3aed;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 4px;
}
.bot-label {
    margin-left: 10px;
    color: #6366f1;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 4px;
}
.pdf-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #ede9fe, #ddd6fe);
    color: #5b21b6;
    border: 1.5px solid #c4b5fd;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 6px;
    margin-left: 120px;
}
.pdf-status {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #ede9fe, #ddd6fe);
    border: 1.5px solid #c4b5fd;
    border-radius: 12px;
    padding: 8px 16px;
    margin-bottom: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #5b21b6;
}
.scroll-btn {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 45px;
    height: 45px;
    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
    color: white !important;
    border-radius: 50%;
    text-align: center;
    line-height: 45px;
    font-size: 1.3rem;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4);
    z-index: 9999;
    display: block !important;
    transition: transform 0.2s, box-shadow 0.2s;
}
.scroll-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(124,58,237,0.5);
}

/* ── Sidebar upload button styled as + ── */
.upload-label {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
    color: white !important;
    border-radius: 14px;
    padding: 12px 18px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(124,58,237,0.3);
    margin-bottom: 8px;
    transition: transform 0.2s;
}
.upload-label:hover { transform: scale(1.02); }

/* Sidebar file uploader clean style */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: linear-gradient(135deg, #7c3aed, #8b5cf6) !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(124,58,237,0.3) !important;
    transition: transform 0.2s !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
    transform: scale(1.02) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
    color: #000000 !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
    color: rgba(255,255,255,0.7) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {
    fill: white !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label {
    color: #000000 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
}


[data-testid="stAlert"] {
    background: linear-gradient(135deg, #ecfdf5, #d1fae5) !important;
    border: 1.5px solid #6ee7b7 !important;
    border-radius: 12px !important;
    color: #065f46 !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1.5px solid #e0d7ff !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.06) !important;
}
[data-testid="stExpander"] summary { color: #7c3aed !important; font-weight: 600 !important; }
.chunk-card {
    background: #faf8ff;
    border: 1.5px solid #ede9fe;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    color: #4b5563;
    line-height: 1.65;
}
/* ── Glassmorphism Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.25) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1.5px solid rgba(255, 255, 255, 0.4) !important;
    box-shadow: 4px 0 24px rgba(124, 58, 237, 0.15) !important;
}

/* ── Sidebar inner content ── */
section[data-testid="stSidebar"] > div {
    background: transparent !important;
    padding: 1.5rem 1rem !important;
}

/* ── Sidebar title ── */
section[data-testid="stSidebar"] h2 {
    font-family: 'Playfair Display', serif !important;
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    margin-bottom: 0.5rem !important;
}

/* ── New Chat button ── */
section[data-testid="stSidebar"] .stButton:first-of-type button {
    background: linear-gradient(135deg, #7c3aed, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 10px 18px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton:first-of-type button:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
}

/* ── Divider ── */
section[data-testid="stSidebar"] hr {
    border-color: rgba(124, 58, 237, 0.2) !important;
    margin: 1rem 0 !important;
}

/* ── Chat list buttons ── */
section[data-testid="stSidebar"] .stButton button {
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.6) !important;
    border-radius: 12px !important;
    color: #2d2250 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 12px !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08) !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255, 255, 255, 0.7) !important;
    border-color: #c4b5fd !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.2) !important;
    transform: translateX(3px) !important;
}

/* ── Active/Primary chat button ── */
section[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(139,92,246,0.2)) !important;
    border: 1.5px solid #a78bfa !important;
    color: #4c1d95 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.2) !important;
}

/* ── Delete button ── */
section[data-testid="stSidebar"] .stButton button[title="🗑"] {
    background: rgba(255, 100, 100, 0.1) !important;
    border: 1.5px solid rgba(255, 100, 100, 0.3) !important;
    color: #dc2626 !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] .stButton button[title="🗑"]:hover {
    background: rgba(255, 100, 100, 0.2) !important;
    transform: scale(1.05) !important;
}

/* ── Upload PDF section ── */
section[data-testid="stSidebar"] h3 {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    color: #4c1d95 !important;
    letter-spacing: 0.03em !important;
    margin-bottom: 0.5rem !important;
}

/* ── File uploader dropzone ── */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: rgba(255, 255, 255, 0.5) !important;
    backdrop-filter: blur(10px) !important;
    border: 2px dashed #a78bfa !important;
    border-radius: 14px !important;
    padding: 12px !important;
    box-shadow: 0 4px 14px rgba(124,58,237,0.1) !important;
    transition: all 0.3s !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(255, 255, 255, 0.7) !important;
    border-color: #7c3aed !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.2) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
    color: #4c1d95 !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
    color: #7c3aed !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {
    fill: #7c3aed !important;
}

/* ── PDF active badge ── */
section[data-testid="stSidebar"] .pdf-active {
    background: rgba(124, 58, 237, 0.12) !important;
    backdrop-filter: blur(10px) !important;
    border: 1.5px solid rgba(167, 139, 250, 0.5) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
}

/* ── Scrollbar in sidebar ── */
section[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 4px !important;
}
section[data-testid="stSidebar"]::-webkit-scrollbar-track {
    background: transparent !important;
}
section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.3) !important;
    border-radius: 10px !important;
}
/* Mobile sidebar toggle button - force black */
@media (max-width: 768px) {
    button[data-testid="stBaseButton-headerNoPadding"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    button[data-testid="stBaseButton-headerNoPadding"] svg {
        fill: #000000 !important;
        stroke: #000000 !important;
    }

    [data-testid="stSidebarCollapseButton"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    [data-testid="stSidebarCollapseButton"] svg {
        fill: #000000 !important;
        stroke: #000000 !important;
    }

    /* Header bar on mobile */
    header[data-testid="stHeader"] {
        background: #f0ebff !important;
    }

    header[data-testid="stHeader"] button svg {
        fill: #000000 !important;
    }
}
hr { border-color: #e0d7ff !important; margin: 1.5rem 0 !important; }
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

st.markdown('<div class="hero-title">🧠 PiscesAI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Upload PDFs or chat like ChatGPT</div>', unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_chats()

if "current_chat" not in st.session_state:
    if not st.session_state.all_chats:
        first_chat_id = str(uuid.uuid4())
        st.session_state.all_chats[first_chat_id] = []
        save_chats(st.session_state.all_chats)
    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]

if "chunks" not in st.session_state:
    st.session_state.chunks = None
if "index" not in st.session_state:
    st.session_state.index = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.all_chats[new_chat_id] = []
        st.session_state.current_chat = new_chat_id
        st.session_state.chunks = None
        st.session_state.index = None
        st.session_state.pdf_name = None
        save_chats(st.session_state.all_chats)
        st.rerun()

    st.divider()

    # ── PDF Upload inside sidebar ────────────────────────────
    st.markdown("### 📎 Upload PDF")
    st.markdown('<p style="color:black; font-weight:700; font-size:0.85rem;">Click below to upload</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "",           # ← empty label
        type=["pdf"],
        key="pdf_uploader",
        label_visibility="collapsed"   # ← hides Streamlit's label completely
    )

    if uploaded_file:
        os.makedirs("uploads", exist_ok=True)
        pdf_path = os.path.join("uploads", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        with st.spinner("⚡ Processing..."):
            text = extract_text(pdf_path)
            chunks = chunk_text(text)
            index, _ = build_index(chunks)
            st.session_state.chunks = chunks
            st.session_state.index = index
            st.session_state.pdf_name = uploaded_file.name
        st.success(f"✅ {uploaded_file.name} ready!")

    # Show active PDF in sidebar
    if st.session_state.pdf_name:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#ede9fe,#ddd6fe);
                    border:1.5px solid #c4b5fd; border-radius:10px;
                    padding:8px 12px; margin-top:8px;
                    font-size:0.82rem; font-weight:600; color:#5b21b6;">
            📄 {st.session_state.pdf_name}<br>
            <span style="color:#7c3aed;font-size:0.75rem;">PDF mode ON</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("❌ Remove PDF", use_container_width=True):
            st.session_state.chunks = None
            st.session_state.index = None
            st.session_state.pdf_name = None
            st.rerun()

    st.divider()

    # ── Chat list ────────────────────────────────────────────
    for chat_id in list(st.session_state.all_chats.keys()):
        messages = st.session_state.all_chats[chat_id]
        user_msgs = [m for m in messages if m["role"] == "user"]
        title = user_msgs[0]["content"][:25] if user_msgs else "New Chat"

        col1, col2 = st.columns([5, 1])
        with col1:
            button_type = "primary" if chat_id == st.session_state.current_chat else "secondary"
            if st.button(title, key=f"chat_{chat_id}", use_container_width=True, type=button_type):
                st.session_state.current_chat = chat_id
                st.rerun()
        with col2:
            if st.button("🗑", key=f"delete_{chat_id}", use_container_width=True):
                del st.session_state.all_chats[chat_id]
                if not st.session_state.all_chats:
                    new_chat_id = str(uuid.uuid4())
                    st.session_state.all_chats[new_chat_id] = []
                    st.session_state.current_chat = new_chat_id
                else:
                    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
                save_chats(st.session_state.all_chats)
                st.rerun()

st.markdown("""
<a href="#bottom" class="scroll-btn">⬇</a>
""", unsafe_allow_html=True)

# ── Display Chat Messages ────────────────────────────────────
messages = st.session_state.all_chats[st.session_state.current_chat]

for msg in messages:
    if msg["role"] == "user":
        if msg.get("pdf"):
            st.markdown(f'<div class="pdf-badge">📄 {msg["pdf"]}</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="user-label">You</div>
            <div class="user-msg">{msg["content"]}</div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="bot-label">PiscesAI</div>
            <div class="bot-msg">{msg["content"]}</div>
        ''', unsafe_allow_html=True)
st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)

# ── Active PDF status bar above input ───────────────────────
if st.session_state.pdf_name:
    st.markdown(f'''
        <div class="pdf-status">
            <span>📄 {st.session_state.pdf_name} is active</span>
            <span style="color:#a78bfa;font-size:0.78rem;">PDF mode ON</span>
        </div>
    ''', unsafe_allow_html=True)

# ── Chat Input (root level = stays at bottom always) ─────────
query = st.chat_input("Ask anything...")

# ── Handle Query ─────────────────────────────────────────────
if query:
    current_messages = st.session_state.all_chats[st.session_state.current_chat]
    chat_history = [(m["role"], m["content"]) for m in current_messages][-6:]

    user_msg_data = {"role": "user", "content": query}
    if st.session_state.pdf_name:
        user_msg_data["pdf"] = st.session_state.pdf_name

    st.session_state.all_chats[st.session_state.current_chat].append(user_msg_data)
    save_chats(st.session_state.all_chats)

    if st.session_state.pdf_name:
        st.markdown(f'<div class="pdf-badge">📄 {st.session_state.pdf_name}</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="user-label">You</div>
        <div class="user-msg">{query}</div>
    ''', unsafe_allow_html=True)

    with st.spinner("🤖 Thinking..."):
        if st.session_state.chunks is not None and st.session_state.index is not None:
            relevant_chunks = retrieve(query, st.session_state.chunks, st.session_state.index, top_k=2)
            answer = ask_llm(query, relevant_chunks, chat_history)
        else:
            relevant_chunks = []
            answer = ask_llm(query, None, chat_history)

    st.markdown(f'''
        <div class="bot-label">PiscesAI</div>
        <div class="bot-msg">{answer}</div>
    ''', unsafe_allow_html=True)
    

    st.session_state.all_chats[st.session_state.current_chat].append({
        "role": "assistant", "content": answer
    })
    save_chats(st.session_state.all_chats)
    

    if relevant_chunks:
        with st.expander("📚 View Source Chunks"):
            for i, chunk in enumerate(relevant_chunks):
                st.markdown(f"""
                    <div class="chunk-card">
                        <b>Chunk {i+1}</b><br><br>{chunk}
                    </div>
                """, unsafe_allow_html=True)

    st.rerun()
