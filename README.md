# AI Job Application Co-Pilot

A multi-agent system designed to automate the generation of tailored job application materials. The system is orchestrated via LangGraph, utilizing a two-phase directed acyclic graph (DAG) to execute specialized agents in parallel. It handles resume rewriting, cover letter generation, web research, interview preparation, and cold outreach drafting.

## Architecture

The orchestration layer is built on LangGraph, defining a stateful graph with checkpointing via MongoDB. Execution is split into two fan-out/fan-in phases to respect data dependencies while maximizing concurrency.

1. **Phase 1 (Data Extraction & Retrieval)**: 
   - **Supervisor Node**: Extracts structured metadata (role, skills, hiring manager) from the job description using `with_structured_output`.
   - **Research Agent**: Scrapes the web using Tavily to compile a company and role-specific briefing.
   - **Resume Agent**: Chunks the user's base resume, embeds it using `all-MiniLM-L6-v2`, stores it in a FAISS vector index, and retrieves the most relevant sections for ATS optimization using Qwen3-Coder.

2. **Phase 2 (Generation)**:
   - **Cover Letter Agent**: Synthesizes the research brief and tailored resume into a personalized cover letter.
   - **Interview Prep Agent**: Generates technical and behavioral (STAR) questions.
   - **Outreach Agent**: Drafts a cold email to the hiring manager.

3. **Control Flow**:
   - The graph utilizes LangGraph's `interrupt()` mechanism to pause execution prior to finalization.
   - A React frontend presents the intermediate state to the user.
   - Upon user approval, the graph resumes via `Command(resume=...)`, triggering the final Tracker node which persists the application to MongoDB, exports DOCX artifacts, and dispatches the outreach email via SMTP.

## Technical Stack

- **Orchestration**: LangGraph, LangChain
- **Backend API**: FastAPI, Uvicorn, Motor (Async MongoDB)
- **Frontend**: React 18, Vite, TypeScript, TailwindCSS
- **LLM Integration**: OpenRouter (`langchain-openrouter`)
- **Vector Store**: FAISS (local fallback), MongoDB Atlas Search (production)
- **Data Parsing**: PyMuPDF (`fitz`), `python-docx`, Playwright, BeautifulSoup
- **Observability**: LangSmith

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for local MongoDB instance)
- API Keys: OpenRouter and Tavily

## Local Development Setup

### 1. Database Initialization

Start the local MongoDB container:

```bash
docker-compose up -d
```

### 2. Backend Setup

Initialize the Python virtual environment and install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Copy the environment template and populate your API keys:

```bash
cp .env.example .env
```

Required environment variables in `backend/.env`:
```text
OPENROUTER_API_KEY=your_openrouter_key
TAVILY_API_KEY=your_tavily_key
JWT_SECRET_KEY=your_jwt_secret_minimum_32_characters
MONGODB_URI=mongodb://localhost:27017
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

### 3. Frontend Setup

Install Node dependencies and start the Vite development server:

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

## Streaming and State Management

The backend multiplexes the output of concurrently running agents into a single Server-Sent Events (SSE) stream. The React frontend demultiplexes these events by inspecting the `agent` key in the JSON payload, rendering the token stream into individual terminal grids in real-time.

User sessions and graph state are persisted in MongoDB. The FastAPI `get_current_user` dependency injects the `user_id` into the `ApplicationState`, enforcing memory isolation across LangGraph threads.
