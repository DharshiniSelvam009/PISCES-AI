import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

MODEL_NAME = "llama-3.1-8b-instant"
MAX_TOKENS = 400
MAX_HISTORY_MESSAGES = 6
MAX_CONTEXT_CHUNKS = 2


def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def build_index(chunks):
    embeddings = embedder.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, embeddings

def retrieve(query, chunks, index, top_k=3):
    query_vec = embedder.encode([query]).astype("float32")
    _, indices = index.search(query_vec, top_k)
    return [chunks[i] for i in indices[0]]


def _trim_chat_history(chat_history, max_messages=MAX_HISTORY_MESSAGES):
    if len(chat_history) <= max_messages:
        return chat_history
    return chat_history[-max_messages:]


def _limit_context_chunks(context_chunks, max_chunks=MAX_CONTEXT_CHUNKS):
    if not context_chunks:
        return []
    return context_chunks[:max_chunks]


def ask_llm(query, context_chunks=None, chat_history=None):
    if chat_history is None:
        chat_history = []
    chat_history = _trim_chat_history(chat_history)
    context_chunks = _limit_context_chunks(context_chunks)

    # ── Build document context block ──────────────────────────
    if context_chunks:
        context = "\n\n".join(context_chunks)
        context_block = f"Document Context (use only if relevant):\n{context}\n\n"
    else:
        context_block = ""

    # ── Inject last assistant reply so model never forgets it ──
    last_assistant = next(
        (content for role, content in reversed(chat_history) if role == "assistant"),
        None
    )
    memory_hint = ""
    if last_assistant:
        memory_hint = f"\n[Your last response was: {last_assistant[:400]}]\n"

    # ── System prompt ──────────────────────────────────────────
    system_prompt = f"""You are a concise, helpful AI assistant with memory of the full conversation.

STRICT RULES:
- ALWAYS read the conversation history AND the memory hint below before answering
- If the user says "in java" / "in python" / "in C" / "in <language>" — immediately translate the LAST code from your memory hint into that language. No questions asked.
- If the user says "simpler" / "shorter" / "brief" / "explain" — shorten or simplify your LAST response from the memory hint
- If the user says "more detail" / "elaborate" / "expand" — give a longer version of your last response
- Keep answers SHORT and CLEAR by default unless the user asks for detail
- For code: give clean code with minimal explanation unless asked
- Use document context only if it is relevant to the question
- Otherwise answer from your general knowledge naturally
- NEVER say "no previous answer exists" — the memory hint always has it{memory_hint}"""

    # ── Build messages with full history ──────────────────────
    messages = [{"role": "system", "content": system_prompt}]

    # Add full conversation history
    for role, content in chat_history:
        messages.append({"role": role, "content": content})

    # Add current user question
    messages.append({
        "role": "user",
        "content": f"{context_block}{query}"
    })

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=0.3   # lower = more focused, less random
    )

    return response.choices[0].message.content