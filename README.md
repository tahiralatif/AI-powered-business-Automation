# AI Co-founder for Hackathon

This project contains an AI-powered business assistant designed for hackathons and startups. The project follows a modern architecture with separate frontend and backend components.

## Project Structure

```
AI-Co-founder_for_hackathon/
├── backend/                 # Backend services and AI agents
│   ├── main.py             # Main orchestrator agent
│   ├── agent_hooks.py      # Agent hooks and middleware
│   ├── custom_tools.py     # Custom tools for agents
│   ├── pyproject.toml      # Project dependencies
│   ├── requirements.txt    # Python requirements
│   ├── .env                # Environment variables
│   ├── .gitignore          # Git ignore rules
│   ├── README.md           # Backend documentation
│   ├── guadrails/          # Input/output validation guardrails
│   ├── handoffagents/      # Specialized AI agents
│   └── tools/              # Utility tools for agents
├── frontend/                # Frontend application
└── README.md               # Project overview (this file)
```

## Backend

The backend contains the AI agent system that provides business assistance through specialized agents for:
- Business plan generation
- Idea generation
- Competitor analysis
- Pitch deck creation

For detailed information about the backend services, see `backend/README.md`.

## Frontend

The frontend directory is reserved for the user interface that will interact with the backend AI services. This will provide a web-based interface for users to access the AI co-founder capabilities.

For information about setting up and running the frontend, see `frontend/README.md` when available.

## Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   WEB_SEARCH_API=your_web_search_api_key
   Search_Engine_ID=your_search_engine_id
   ```

4. Run the application:
   ```bash
   python main.py
   ```