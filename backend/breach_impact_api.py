"""
FastAPI Integration for Breach Impact Prediction Workflow

This module provides REST API endpoints to interact with the LangGraph workflow
for GDPR breach impact prediction.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio

from backend.breach_impact_workflow import predict_breach_impact

app = FastAPI(title="GDPR Breach Impact Predictor API", version="1.0.0")

class BreachCaseInput(BaseModel):
    case_description: str
    lawfulness_of_processing: str
    data_subject_rights_compliance: str
    risk_management_and_safeguards: str
    accountability_and_governance: str

class SimilarCaseOutput(BaseModel):
    id: str
    company: str
    description: str
    fine: int
    similarity: int
    explanation_of_similarity: str
    date: str
    authority: str

class PredictionOutput(BaseModel):
    predicted_fine: int
    explanation_for_fine: str

class BreachImpactResponse(BaseModel):
    similar_cases: List[SimilarCaseOutput]
    prediction_result: PredictionOutput
    error: str = None

@app.post("/predict-breach-impact", response_model=BreachImpactResponse)
async def predict_impact(case_input: BreachCaseInput):
    """
    Predict the financial impact of a GDPR breach case
    
    Args:
        case_input: Breach case details and classifications
        
    Returns:
        Similar cases and predicted fine amount
    """
    try:
        # Validate classifications
        valid_lawfulness = [
            "lawful_and_appropriate_basis", "lawful_but_principle_violation", 
            "no_valid_basis", "exempt_or_restricted"
        ]
        valid_rights = [
            "full_compliance", "partial_compliance", 
            "non_compliance", "not_triggered"
        ]
        valid_risk = [
            "proactive_safeguards", "reactive_only", 
            "insufficient_protection", "not_applicable"
        ]
        valid_governance = [
            "fully_accountable", "partially_accountable", 
            "not_accountable", "not_required"
        ]
        
        if case_input.lawfulness_of_processing not in valid_lawfulness:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid lawfulness_of_processing. Must be one of: {valid_lawfulness}"
            )
        
        if case_input.data_subject_rights_compliance not in valid_rights:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_subject_rights_compliance. Must be one of: {valid_rights}"
            )
            
        if case_input.risk_management_and_safeguards not in valid_risk:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid risk_management_and_safeguards. Must be one of: {valid_risk}"
            )
            
        if case_input.accountability_and_governance not in valid_governance:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid accountability_and_governance. Must be one of: {valid_governance}"
            )
        
        # Run the workflow
        result = await predict_breach_impact(
            case_description=case_input.case_description,
            lawfulness_of_processing=case_input.lawfulness_of_processing,
            data_subject_rights_compliance=case_input.data_subject_rights_compliance,
            risk_management_and_safeguards=case_input.risk_management_and_safeguards,
            accountability_and_governance=case_input.accountability_and_governance
        )
        
        # Convert result to response model
        if "error" in result:
            return BreachImpactResponse(
                similar_cases=[],
                prediction_result=result["prediction_result"],
                error=result["error"]
            )
        else:
            return BreachImpactResponse(
                similar_cases=[SimilarCaseOutput(**case) for case in result["similar_cases"]],
                prediction_result=PredictionOutput(**result["prediction_result"])
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "GDPR Breach Impact Predictor API is running"}

@app.get("/classifications")
async def get_valid_classifications():
    """Get all valid classification values"""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
