"""
Integration module for the Breach Impact Prediction Workflow

This module integrates the LangGraph workflow with your existing FastAPI backend.
Add this to your main backend application to expose the breach prediction functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio
import sys
import os

# Add the project root to the path so we can import the workflow
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from breach_impact_workflow import predict_breach_impact

router = APIRouter(prefix="/api", tags=["breach-prediction"])

class BreachPredictionRequest(BaseModel):
    case_description: str
    lawfulness_of_processing: str
    data_subject_rights_compliance: str
    risk_management_and_safeguards: str
    accountability_and_governance: str

class SimilarCase(BaseModel):
    id: str
    company: str
    description: str
    fine: int
    similarity: int
    explanation_of_similarity: str
    date: str
    authority: str

class PredictionResult(BaseModel):
    predicted_fine: int
    explanation_for_fine: str

class BreachPredictionResponse(BaseModel):
    similar_cases: List[SimilarCase]
    prediction_result: PredictionResult
    error: str = None

@router.post("/predict-breach-impact", response_model=BreachPredictionResponse)
async def predict_breach_impact_endpoint(request: BreachPredictionRequest):
    """
    Predict the financial impact of a GDPR breach using LangGraph workflow
    
    This endpoint integrates with your existing frontend BreachImpactPredictor component.
    """
    try:
        result = await predict_breach_impact(
            case_description=request.case_description,
            lawfulness_of_processing=request.lawfulness_of_processing,
            data_subject_rights_compliance=request.data_subject_rights_compliance,
            risk_management_and_safeguards=request.risk_management_and_safeguards,
            accountability_and_governance=request.accountability_and_governance
        )
        
        if "error" in result:
            return BreachPredictionResponse(
                similar_cases=[],
                prediction_result=result["prediction_result"],
                error=result["error"]
            )
        
        return BreachPredictionResponse(
            similar_cases=[SimilarCase(**case) for case in result["similar_cases"]],
            prediction_result=PredictionResult(**result["prediction_result"])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/breach-classifications")
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

# Instructions for integration with main.py:
"""
To integrate this with your existing backend/main.py, add these lines:

from breach_integration import router as breach_router

app.include_router(breach_router)

Then your frontend can call:
- POST /api/predict-breach-impact
- GET /api/breach-classifications

The response format matches exactly what your BreachImpactPredictor.tsx component expects.
"""
