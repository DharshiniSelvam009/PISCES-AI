✨ Features

💬 Chat like ChatGPT — Ask any general question
📄 Chat with PDFs — Upload a PDF and ask questions about it
🧠 Memory — Remembers previous messages in the conversation
🔄 Follow-up support — Say "in Java", "simpler", "explain" and it understands
💾 Persistent chat history — Chats are saved across sessions
🗂️ Multiple chats — Create, switch, and delete chats like ChatGPT
🎨 Beautiful UI — Light purple gradient theme with chat bubbles
⚡ Fast responses — Powered by Groq's free API


🖥️ Demo
You:      write a palindrome code in python
PiscesAI: def is_palindrome(s): return s == s[::-1]

You:      in java
PiscesAI: public boolean isPalindrome(String s) { ... }

You:      explain this pdf
PiscesAI: Based on the document: ...

🛠️ Tech Stack
ComponentTechnologyFrontendStreamlitLLMLLaMA 3.1 8B via Groq API (Free)Embeddingssentence-transformers (all-MiniLM-L6-v2)Vector StoreFAISSPDF ParsingPyMuPDF (fitz)LanguagePython 3.10+

📁 Project Structure
rag_project/
│
├── app.py              ← Streamlit UI & chat logic
├── rag.py              ← RAG pipeline (extract, chunk, embed, retrieve, LLM)
├── .env                ← API keys (never commit this!)
├── all_chats.json      ← Saved chat history (auto-created)
├── uploads/            ← Uploaded PDFs (auto-created)
├── requirements.txt    ← Python dependencies


Get your free Groq API key

Go to 👉 https://console.groq.com
Sign up and click API Keys → Create API Key
Copy your key



📦 Requirements
Create a requirements.txt file:
txtstreamlit
faiss-cpu
sentence-transformers
pymupdf
groq
python-dotenv
numpy


💡 How It Works
Normal Chat Mode
User Question → LLM (LLaMA 3.1) → Answer
PDF / RAG Mode
PDF Upload → Extract Text → Split into Chunks
                                    ↓
User Question → Embed Query → FAISS Search → Top Chunks
                                                  ↓
                              LLM (LLaMA 3.1 + Context) → Answer
