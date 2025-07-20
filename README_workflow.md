# GDPR Breach Impact Prediction Workflow

This LangGraph-based agentic workflow predicts the financial impact of GDPR data breaches by analyzing similar precedent cases from a Weaviate vector database.

## 🏗️ Architecture

The workflow consists of three main steps implemented as LangGraph nodes:

1. **Search Similar Cases**: Searches Weaviate for the top 50 similar cases using hybrid search
2. **Similarity Analysis**: Five parallel agents analyze the top 5 unique cases for detailed similarity 
3. **Combine Results**: Combines analyses to predict fine amount and generate similar cases list

## 📊 Input Format

```python
{
    "case_description": str,  # Description of the breach case
    "lawfulness_of_processing": str,  # One of the classification options below
    "data_subject_rights_compliance": str,
    "risk_management_and_safeguards": str, 
    "accountability_and_governance": str
}
```

### Classification Options

#### 1. Lawfulness of Processing
- `lawful_and_appropriate_basis`
- `lawful_but_principle_violation`
- `no_valid_basis`
- `exempt_or_restricted`

#### 2. Data Subject Rights Compliance
- `full_compliance`
- `partial_compliance`
- `non_compliance`
- `not_triggered`

#### 3. Risk Management and Safeguards
- `proactive_safeguards`
- `reactive_only`
- `insufficient_protection`
- `not_applicable`

#### 4. Accountability and Governance
- `fully_accountable`
- `partially_accountable`
- `not_accountable`
- `not_required`

## 📤 Output Format

```python
{
    "similar_cases": [
        {
            "id": str,
            "company": str,
            "description": str,
            "fine": int,
            "similarity": int,  # 0-100 score
            "explanation_of_similarity": str,
            "date": str,
            "authority": str
        }
    ],
    "prediction_result": {
        "predicted_fine": int,  # Amount in EUR
        "explanation_for_fine": str
    }
}
```

## 🚀 Usage

### Direct Python Usage

```python
import asyncio
from breach_impact_workflow import predict_breach_impact

async def main():
    result = await predict_breach_impact(
        case_description="Healthcare breach affecting 50,000 patients...",
        lawfulness_of_processing="no_valid_basis",
        data_subject_rights_compliance="non_compliance",
        risk_management_and_safeguards="insufficient_protection",
        accountability_and_governance="not_accountable"
    )
    
    print(f"Predicted Fine: €{result['prediction_result']['predicted_fine']:,}")
    print(f"Similar Cases: {len(result['similar_cases'])}")

asyncio.run(main())
```

### FastAPI Server

```bash
# Start the API server
poetry run python breach_impact_api.py

# Or using uvicorn directly
poetry run uvicorn breach_impact_api:app --host 0.0.0.0 --port 8001
```

### API Endpoints

- `POST /predict-breach-impact`: Main prediction endpoint
- `GET /health`: Health check
- `GET /classifications`: Get valid classification values

### Example API Call

```python
import requests

data = {
    "case_description": "Fintech company API breach exposing 100K customer records",
    "lawfulness_of_processing": "no_valid_basis",
    "data_subject_rights_compliance": "non_compliance", 
    "risk_management_and_safeguards": "insufficient_protection",
    "accountability_and_governance": "not_accountable"
}

response = requests.post("http://localhost:8001/predict-breach-impact", json=data)
result = response.json()
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
poetry run python test_workflow.py
```

This tests:
- LangGraph workflow execution
- FastAPI integration
- Input validation
- Error handling

## 📋 Requirements

- Python 3.10+
- OpenAI API Key
- Weaviate Cloud instance with Precedent collection
- Dependencies managed via Poetry

## 🔧 Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key
WEAVIATE_URL=your_weaviate_cloud_url
WEAVIATE_API_KEY=your_weaviate_api_key
```

## 📁 File Structure

```
├── breach_impact_workflow.py   # Main LangGraph workflow
├── breach_impact_api.py        # FastAPI integration
├── test_workflow.py           # Test suite
├── pyproject.toml            # Poetry dependencies
└── README_workflow.md        # This documentation
```

## 🤖 Agent Behavior

### Search Agent
- Uses hybrid search combining vector similarity and keyword matching
- Searches on combined case description and classifications
- Returns top 50 candidates, filtered to 5 unique precedent cases

### Similarity Analysis Agents
- Each agent analyzes one precedent case
- Retrieves detailed case chunks from Weaviate for deep analysis
- Uses GPT-4 to assess similarity across multiple dimensions:
  - Violation type and circumstances
  - GDPR articles involved
  - Company size and sector
  - Regulatory authority patterns
  - Severity factors

### Prediction Agent
- Combines similarity analyses with weighted scoring
- Considers regulatory trends and inflation
- Analyzes aggravating/mitigating factors
- Generates detailed reasoning for the prediction

## ⚡ Performance

- Typical execution time: 30-60 seconds
- Concurrent similarity analysis for 5 cases
- Efficient vector search with metadata filtering
- Configurable limits and timeouts

## 🔍 Error Handling

- Graceful fallbacks for API failures
- Default similarity scores on analysis errors
- Comprehensive error messages
- Validation of input classifications

## 🎯 Integration with Frontend

The workflow is designed to integrate seamlessly with the React frontend's `BreachImpactPredictor` component. The API returns data in the exact format expected by the frontend interface.

## 🧩 Extension Points

- Add more sophisticated similarity algorithms
- Implement caching for repeated queries  
- Add support for multi-language case analysis
- Include more regulatory factors in predictions
- Add confidence intervals for predictions
