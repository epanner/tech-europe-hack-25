from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .evaluation_service import EvaluationService
from .case_gathering_agent import CaseGatheringAgent
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

evaluation_service = EvaluationService(api_key=os.getenv("OPENAI_API_KEY"))
case_gathering_agent = CaseGatheringAgent(api_key=os.getenv("OPENAI_API_KEY"))

# Store active conversations (in production, use Redis or database)
active_conversations: Dict[str, List[Dict[str, str]]] = {}
conversation_iterations: Dict[str, int] = {}  # Track iteration count per conversation

# Allow all CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartConversationRequest(BaseModel):
    initial_description: Optional[str] = ""
    conversation_id: Optional[str] = None


class ContinueConversationRequest(BaseModel):
    conversation_id: str
    user_response: str


@app.post("/api/start-case-gathering")
async def start_case_gathering(request: StartConversationRequest):
    """Start a new case gathering conversation with streaming responses"""
    
    import uuid
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Initialize conversation with system message and iteration tracking
    conversation_iterations[conversation_id] = 1
    system_instructions_with_context = case_gathering_agent.get_system_instructions_with_context(1)
    
    active_conversations[conversation_id] = [
        {"role": "system", "content": system_instructions_with_context}
    ]
    
    if request.initial_description:
        active_conversations[conversation_id].append({
            "role": "user", 
            "content": f"I need help classifying a GDPR breach case. Here's what I know so far: {request.initial_description}"
        })
    else:
        active_conversations[conversation_id].append({
            "role": "user", 
            "content": "I need help classifying a GDPR breach case. I'd like to provide information about the incident."
        })

    async def generate_stream():
        yield f"data: {json.dumps({'type': 'conversation_id', 'data': conversation_id})}\n\n"
        
        async for chunk in case_gathering_agent.start_conversation(request.initial_description):
            yield f"data: {chunk}\n\n"
        
        yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"

    return StreamingResponse(
        generate_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.post("/api/continue-case-gathering")
async def continue_case_gathering(request: ContinueConversationRequest):
    """Continue an existing case gathering conversation"""
    
    if request.conversation_id not in active_conversations:
        return JSONResponse(
            status_code=404, 
            content={"error": "Conversation not found"}
        )
    
    # Increment iteration count
    if request.conversation_id not in conversation_iterations:
        conversation_iterations[request.conversation_id] = 1
    conversation_iterations[request.conversation_id] += 1
    
    current_iteration = conversation_iterations[request.conversation_id]
    
    messages = active_conversations[request.conversation_id]
    
    # Update system message with new iteration context
    system_instructions_with_context = case_gathering_agent.get_system_instructions_with_context(current_iteration)
    messages[0] = {"role": "system", "content": system_instructions_with_context}
    
    async def generate_stream():
        async for chunk in case_gathering_agent.continue_conversation(messages, request.user_response):
            yield f"data: {chunk}\n\n"
        
        yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"

    return StreamingResponse(
        generate_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.delete("/api/case-gathering/{conversation_id}")
async def end_case_gathering(conversation_id: str):
    """End a case gathering conversation and clean up resources"""
    if conversation_id in active_conversations:
        del active_conversations[conversation_id]
        if conversation_id in conversation_iterations:
            del conversation_iterations[conversation_id]
        return JSONResponse(content={"message": "Conversation ended successfully"})
    else:
        return JSONResponse(
            status_code=404, 
            content={"error": "Conversation not found"}
        )


@app.post("/api/evaluate")
async def evaluate(request: Request):
    data = await request.json()
    if not data or 'case_description' not in data:
        return JSONResponse(status_code=400, content={"error": "Missing 'case_description' in request body"})
    case_description = data['case_description']
    evaluation_result = evaluation_service.get_evaluation(case_description)
    if evaluation_result:
        try:
            return JSONResponse(content=evaluation_result.model_dump())
        except Exception as e:
            print(f"Error in model dump: {e}")
            return JSONResponse(status_code=500, content={"error": "Failed to process evaluation result"})
    else:
        return JSONResponse(status_code=500, content={"error": "Failed to get case evaluation from OpenAI API. Check server logs for details."})


@app.get("/api/case-gathering/{conversation_id}")
async def get_case_gathering_status(conversation_id: str):
    """Get the current status and classification of a case gathering conversation"""
    if conversation_id not in active_conversations:
        return JSONResponse(
            status_code=404,
            content={"error": "Conversation not found"}
        )
    
    # Get current classification if available
    current_classification = case_gathering_agent.get_current_classification()
    
    response_data = {
        "conversation_id": conversation_id,
        "conversation_complete": current_classification is not None,
        "message_count": len(active_conversations[conversation_id]),
    }
    
    if current_classification:
        response_data["classification"] = current_classification.model_dump()
    
    return JSONResponse(content=response_data)