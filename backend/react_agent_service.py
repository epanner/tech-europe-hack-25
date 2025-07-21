from typing import Dict
from uuid import uuid4
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import ChatRequest, ChatResponse
from backend.ReAct import OpenAIGDPRReActAgentSync

from load_dotenv import load_dotenv


app = FastAPI(
    title="GDPR Compliance Data Collector",
    description="Interactive GDPR compliance information collector using OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_sessions: Dict[str, OpenAIGDPRReActAgentSync] = {}

def get_or_create_agent(session_id: str) -> OpenAIGDPRReActAgentSync:
    """Get existing agent or create new one for session"""
    if session_id not in agent_sessions:
        agent_sessions[session_id] = OpenAIGDPRReActAgentSync(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4"
        )
    return agent_sessions[session_id]


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        load_dotenv()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid4())
        
        # Get or create agent for this session
        agent = get_or_create_agent(session_id)
        
        # Handle reset command
        if request.message.lower() == 'reset':
            agent.reset()
            return ChatResponse(
                response="🔄 Please describe your data breach incident.",
                session_id=session_id,
                is_complete=False,
                collected_data={},
                progress={"collected": 0, "total": 6, "percentage": 0}
            )
        
        # Process user input
        agent_response = agent.process_user_input(request.message)
        
        # Check if collection is complete
        final_model = agent.get_company_input_model()
        is_complete = final_model is not None
        
        # Calculate progress
        total_fields = 5
        collected_fields = len(agent.collected_data)
        progress = {
            "collected": collected_fields,
            "total": total_fields,
            "percentage": (collected_fields / total_fields) * 100,
            "missing_fields": list(set(["user_input", "data_type", "lawfulness_of_processing", 
                                       "data_subject_rights_compliance", "risk_management_and_safeguards", 
                                       "accountability_and_governance"]) - set(agent.collected_data.keys()))
        }
        return ChatResponse(
            response=agent_response,
            session_id=session_id,
            is_complete=is_complete,
            collected_data=agent.collected_data.copy(),
            progress=progress,
            final_model=final_model.model_dump() if final_model else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/")
async def root():
    """
    API info endpoint
    """
    return {
        "message": "GDPR Compliance Data Collector API",
        "endpoints": {
            "POST /chat": "Main chat endpoint for data collection",
            "GET /session/{session_id}/status": "Get session status",
            "DELETE /session/{session_id}": "Delete session",
            "GET /sessions": "List all sessions"
        },
        "usage": "Send POST requests to /chat with message and optional session_id"
    }
