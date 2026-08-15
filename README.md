# TruthLens
**A Multi-Modal Disinformation Detection and Propagation Tracker**

TruthLens is a powerful, AI-driven fact-checking platform that analyzes articles, text, and images to determine their credibility. By combining local Large Language Models (LLMs) with live web corroboration, TruthLens provides users with a comprehensive, transparent, and explainable **Credibility Scorecard**.

## 🚀 Features
- **Local AI Analysis:** Uses Ollama and `qwen3:8b` locally to ensure privacy and avoid API costs. The AI extracts context, relevant facts, tone, and clickbait patterns.
- **Live Web Verification:** Automatically searches the live web using the Tavily API to corroborate claims against 50+ trusted news sources (like Reuters, BBC, AP).
- **Ad & Clickbait Detection:** Analyzes raw HTML to detect low-quality ad networks (Taboola, Outbrain) and excessive ad density.
- **Multi-Modal Input:** Supports direct URL parsing, raw text input, and image uploads.
- **Premium Frontend:** A beautiful, responsive Next.js dashboard built with a clean, sober editorial aesthetic.
- **Downloadable PDF Reports:** Export your credibility scorecard instantly.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
1. [Python 3.10+](https://www.python.org/downloads/)
2. [Node.js (v18+) and npm](https://nodejs.org/)
3. [Ollama](https://ollama.com/)

### Ollama Setup
You must have the `qwen3:8b` model pulled locally.
```bash
# Start the ollama server if it isn't running
ollama serve

# Open a new terminal and pull the model (this is a large download)
ollama run qwen3:8b
```

---

## ⚙️ Backend Setup (Python)

1. **Navigate to the root directory:**
   ```bash
   cd articledetection
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - On **Mac/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up Environment Variables:**
   Create a `.env` file in the root directory (where `main.py` is) and add your Tavily API key:
   ```env
   # .env
   TAVILY_API_KEY=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
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen3:8b
   ```

6. **Test the Backend (CLI Mode):**
   ```bash
   python main.py --url "https://www.bbc.com/news"
   ```

---

## 💻 Frontend Setup (Next.js)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the Development Server:**
   ```bash
   npm run dev
   ```

4. **Open the App:**
   Open your browser and navigate to `http://localhost:3000`.

---

## 🧠 How it Works

When you submit an article via the TruthLens frontend:
1. **The API Route** (`frontend/app/api/analyze/route.ts`) spawns a child process running `python main.py --json --url <URL>`.
2. **Extraction (`trafilatura`)**: The backend strips away menus and popups, isolating the pure article text and analyzing ad structures.
3. **AI Context (`Ollama`)**: The local LLM processes the text to understand the context, filtering out irrelevant fluff and identifying core claims.
4. **Corroboration (`Tavily`)**: The backend searches the live web for those core claims, checking if highly trusted Tier-1 sources (like Reuters) are reporting the same facts.
5. **Scorecard Generation**: A final score out of 100 is calculated, applying penalties for clickbait and lack of corroboration. The JSON is sent back to the Next.js frontend to render the beautiful UI.

*Note: Because the AI runs locally on your hardware, analysis can take anywhere from 2 to 10 minutes depending on your CPU/GPU and the length of the article.*
