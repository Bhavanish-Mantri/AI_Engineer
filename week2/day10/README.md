# AI-Powered macOS Simulation Portfolio

A premium, state-of-the-art developer portfolio simulated as a fully responsive macOS desktop environment. Built using **React (Vite)** on the frontend and **FastAPI** on the backend, integrated with the **Groq API (Llama 3.3)** for structured resume-based conversational AI.

---

## 🚀 Key Features

* **Desktop Environment**: Fully state-driven window management with drag-and-drop support, window minimization/maximization, focus tracking, and z-index ordering.
* **Safari Browser Simulation**: Tabbed navigation showcasing:
  * **📂 Projects & Prototypes**: Full-stack and generative AI cards with quick-actions to open local directories or query the AI assistant.
  * **🏆 Achievements & Milestones**: Highlights including scholarships, LeetCode, and certifications.
* **Ask AI (Chat Widget)**: Conversational chat assistant connected to a FastAPI backend that uses RAG / resume content to answer questions in real time.
* **Terminal Simulator**: Fully functional monospace CLI environment supporting standard commands (`help`, `about`, `projects`, `skills`, `contact`, `neofetch`, `clear`).
* **Resume.pdf Viewer**: Multi-section resume view with sidebar scroll-to-view navigation and a local resume download button.
* **Dynamic Menu Bar & Dock**: Interactive clock, status indicators, active application tracking, and bouncing dock animations.

---

## 📂 Project Structure

```text
day10/
├── backend/
│   ├── main.py            # FastAPI Application & Groq API Client
│   ├── Resume.pdf         # Raw resume PDF for backend search
│   └── resume_text.txt    # Extracted candidate resume context
├── frontend/
│   ├── public/            # Static assets (Resume.pdf, wallpaper)
│   ├── src/
│   │   ├── assets/        # Profile pictures and project assets
│   │   ├── App.jsx        # Core desktop UI and state manager
│   │   ├── App.css        # Glassmorphic layout stylesheets
│   │   ├── index.css      # Design tokens and global transitions
│   │   └── main.jsx       # React entry point
│   ├── package.json       # Frontend dependencies (lucide-react, etc.)
│   └── vite.config.js     # Dev server configuration (bound to port 3000)
├── pyproject.toml         # Python dependency definitions
└── README.md              # Project documentation
```

---

## 🛠️ Setup & Running

### 1. Backend Setup (FastAPI)
Navigate to the `backend` directory, set up your Groq API Key, and start the FastAPI reload server.

```bash
cd backend
# Create a .env file and add your Groq API key:
# GROQ_API_KEY=gsk_...

# Run the API server:
uv run uvicorn main:app --reload
```
The backend API server will run at `http://127.0.0.1:8000`.

### 2. Frontend Setup (React + Vite)
Open a new terminal, navigate to the `frontend` directory, install dependencies, and start the development server.

```bash
cd frontend
# Install dependencies:
npm install

# Run Vite dev server:
npm run dev
```
The web application will open at **[http://localhost:3000](http://localhost:3000)**.

---

## 🛡️ License
This project is open-source and available under the MIT License.
