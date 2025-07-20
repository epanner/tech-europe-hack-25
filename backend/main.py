from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from evaluation_service import EvaluationService
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = FastAPI()

evaluation_service = EvaluationService(api_key=os.getenv("OPENAI_API_KEY"))

# Allow all CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        
        return JSONResponse(content=result)
        
    except ImportError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Workflow not available: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )

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