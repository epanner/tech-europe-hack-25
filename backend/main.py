from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from evaluation_service import EvaluationService
from case_gathering_agent import CaseGatheringAgent
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import sys
import uvicorn
import re
from dotenv import load_dotenv
import openai
from case_gathering_agent import BreachInfo

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = FastAPI()

evaluation_service = EvaluationService(api_key=os.getenv("OPENAI_API_KEY"))
case_gathering_agent = CaseGatheringAgent(api_key=os.getenv("OPENAI_API_KEY"))

# Store active conversations (in production, use Redis or database)
active_conversations: Dict[str, List[Dict[str, str]]] = {}
conversation_iterations: Dict[str, int] = {}  # Track iteration count per conversation
conversation_classifications: Dict[str, Any] = {}  # Store classifications per conversation

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
            # Store classification if received
            try:
                chunk_data = json.loads(chunk)
                if chunk_data.get('type') == 'classification_complete' and chunk_data.get('data'):
                    conversation_classifications[conversation_id] = chunk_data['data']
            except:
                pass  # Ignore parsing errors for non-JSON chunks
                
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
            # Store classification if received
            try:
                chunk_data = json.loads(chunk)
                if chunk_data.get('type') == 'classification_complete' and chunk_data.get('data'):
                    conversation_classifications[request.conversation_id] = chunk_data['data']
            except:
                pass  # Ignore parsing errors for non-JSON chunks
                
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
        if conversation_id in conversation_classifications:
            del conversation_classifications[conversation_id]
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
    
    messages = active_conversations[conversation_id]
    current_iteration = conversation_iterations.get(conversation_id, 1)
    current_classification = conversation_classifications.get(conversation_id)
    
    # Extract user messages for case description
    user_messages = [msg['content'] for msg in messages if msg['role'] == 'user']
    case_description = " ".join(user_messages) if user_messages else ""
    
    # If turn count is above 4 and no classification exists, force classification
    if current_iteration > 2 and current_classification is None:
        try:
            # Create conversation text for analysis
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            # Use openai.responses.parse with BreachInfo model like in the notebook
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            classification_prompt = f"""Based on the following conversation about a GDPR breach incident, please provide a comprehensive classification across the 4 key dimensions.

Conversation History:
{conversation_text}

Please analyze the conversation and classify the breach case based on the available information. Make reasonable inferences where information is incomplete."""

            # Use openai.responses.parse exactly like in the notebook
            response = client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": "You are an expert GDPR case analysis assistant. Analyze the conversation history and provide a structured classification of the breach incident based on the 4 key dimensions. Make reasonable inferences where information is incomplete."},
                    {"role": "user", "content": classification_prompt}
                ],
                text_format=BreachInfo,
            )
            
            # Extract the structured classification from parsed output
            forced_classification = response.output_parsed.model_dump()
            # Store the forced classification
            conversation_classifications[conversation_id] = forced_classification
            current_classification = forced_classification
            
        except Exception as e:
            print(f"Error forcing classification: {e}")
            # Fallback to default classification if OpenAI call fails
            current_classification = {
                "case_description": case_description or "GDPR breach case from conversation",
                "lawfulness_of_processing": "lawful_and_appropriate_basis",
                "data_subject_rights_compliance": "partial_compliance", 
                "risk_management_and_safeguards": "insufficient_protection",
                "accountability_and_governance": "partially_accountable"
            }
            conversation_classifications[conversation_id] = current_classification
    
    response_data = {
        "conversation_id": conversation_id,
        "conversation_complete": current_classification is not None,
        "message_count": len(messages),
        "iteration_count": current_iteration,
        "case_description": case_description,
        "conversation_history": [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in messages if msg["role"] != "system"
        ]
    }
    
    # Include full classification details if available
    if current_classification:
        response_data["classification"] = current_classification
        response_data["classifications"] = {
            "lawfulness_of_processing": current_classification.get("lawfulness_of_processing"),
            "data_subject_rights_compliance": current_classification.get("data_subject_rights_compliance"),
            "risk_management_and_safeguards": current_classification.get("risk_management_and_safeguards"),
            "accountability_and_governance": current_classification.get("accountability_and_governance")
        }
        response_data["case_summary"] = current_classification.get("case_description", case_description)
    
    return JSONResponse(content=response_data)

# Breach Impact Prediction Endpoint
@app.post("/api/predict-breach-impact")
async def predict_breach_impact_endpoint(request: Request):
    """Predict GDPR breach impact using LangGraph workflow"""
    try:
        # Import here to avoid issues if workflow dependencies aren't available
        from breach_impact_workflow import predict_breach_impact
        
        data = await request.json()
        
        # Validate required fields
        required_fields = [
            'case_description', 'lawfulness_of_processing', 
            'data_subject_rights_compliance', 'risk_management_and_safeguards',
            'accountability_and_governance'
        ]
        
        for field in required_fields:
            if field not in data:
                return JSONResponse(
                    status_code=400, 
                    content={"error": f"Missing required field: {field}"}
                )
        
        # Run the workflow
        result = await predict_breach_impact(
            case_description=data['case_description'],
            lawfulness_of_processing=data['lawfulness_of_processing'],
            data_subject_rights_compliance=data['data_subject_rights_compliance'],
            risk_management_and_safeguards=data['risk_management_and_safeguards'],
            accountability_and_governance=data['accountability_and_governance']
        )
        
        # Ensure the response always has the required structure
        if not result.get('similar_cases'):
            result['similar_cases'] = []
        
        if not result.get('prediction_result'):
            result['prediction_result'] = {
                "predicted_fine": 1000000,
                "explanation_for_fine": "Default prediction - unable to analyze similar cases"
            }
        
        # Validate that each similar case has all required fields
        validated_cases = []
        for case in result.get('similar_cases', []):
            validated_case = {
                "id": str(case.get("id", "unknown")),
                "company": str(case.get("company", "Unknown Company")),
                "description": str(case.get("description", "No description available")),
                "fine": int(case.get("fine", 0)),
                "similarity": int(case.get("similarity", 0)),
                "explanation_of_similarity": str(case.get("explanation_of_similarity", "No explanation available")),
                "date": str(case.get("date", "Unknown")),
                "authority": str(case.get("authority", "Unknown Authority"))
            }
            validated_cases.append(validated_case)
        
        result['similar_cases'] = validated_cases
        
        return JSONResponse(content=result)
        
    except ImportError as e:
        # Fallback to mock data if workflow is not available
        mock_result = {
            "similar_cases": [
                {
                    "id": "fallback_1",
                    "company": "Meta Platforms Ireland",
                    "description": "Cross-border data transfers without adequate safeguards",
                    "fine": 1200000000,
                    "similarity": 75,
                    "explanation_of_similarity": "Both cases involve cross-border data transfers and insufficient safeguards",
                    "date": "2023-05-22",
                    "authority": "Irish DPC"
                },
                {
                    "id": "fallback_2",
                    "company": "Amazon Europe Core",
                    "description": "Inappropriate data processing for advertising purposes",
                    "fine": 746000000,
                    "similarity": 65,
                    "explanation_of_similarity": "Similar violations regarding consent and data processing purposes",
                    "date": "2021-07-30",
                    "authority": "Luxembourg CNPD"
                }
            ],
            "prediction_result": {
                "predicted_fine": 500000000,
                "explanation_for_fine": "Based on similar high-impact cases, estimated fine considering severity factors (fallback prediction)"
            }
        }
        return JSONResponse(content=mock_result)
        
    except Exception as e:
        # Enhanced error handling with fallback
        print(f"Prediction error: {str(e)}")
        
        fallback_result = {
            "similar_cases": [
                {
                    "id": "error_fallback_1",
                    "company": "Example Corporation",
                    "description": "Data breach with similar characteristics",
                    "fine": 1000000,
                    "similarity": 50,
                    "explanation_of_similarity": "General similarity based on breach type (error fallback)",
                    "date": "2023-01-01", 
                    "authority": "Data Protection Authority"
                }
            ],
            "prediction_result": {
                "predicted_fine": 1000000,
                "explanation_for_fine": f"Error in detailed analysis: {str(e)}. Using conservative estimate."
            },
            "error": f"Prediction failed: {str(e)}"
        }
        
        return JSONResponse(content=fallback_result)

@app.get("/api/breach-classifications")
async def get_breach_classifications():
    """Get valid classification values for breach prediction"""
    return {
        "lawfulness_of_processing": [
            "lawful_and_appropriate_basis", "lawful_but_principle_violation", 
            "no_valid_basis", "exempt_or_restricted"
        ],
        "data_subject_rights_compliance": [
            "full_compliance", "partial_compliance", 
            "non_compliance", "not_triggered"
        ],
        "risk_management_and_safeguards": [
            "proactive_safeguards", "reactive_only", 
            "insufficient_protection", "not_applicable"
        ],
        "accountability_and_governance": [
            "fully_accountable", "partially_accountable", 
            "not_accountable", "not_required"
        ]
    }

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
