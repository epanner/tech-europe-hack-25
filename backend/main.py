from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from evaluation_service import EvaluationService
import os
from dotenv import load_dotenv

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
    evaluation_result = await evaluation_service.get_evaluation(case_description)
    if evaluation_result:
        try:
            return JSONResponse(content=evaluation_result.model_dump())
        except Exception as e:
            print(f"Error in model dump: {e}")
            return JSONResponse(status_code=500, content={"error": "Failed to process evaluation result"})
    else:
        return JSONResponse(status_code=500, content={"error": "Failed to get case evaluation from OpenAI API. Check server logs for details."})