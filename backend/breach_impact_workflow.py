"""
LangGraph Agentic Workflow for GDPR Breach Impact Prediction

This workflow receives a case description and GDPR classifications, then:
1. Searches Weaviate for similar precedent cases
2. Analyzes similarity for each case using specialized agents
3. Combines results to predict financial impact

Authors: Tech Europe Hack Team
Date: July 2025
"""

import os
import asyncio
from typing import List, Dict, Any, TypedDict, Annotated
from dataclasses import dataclass
from datetime import datetime

import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import MetadataQuery
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Initialize OpenAI client
llm = ChatOpenAI(
    model="gpt-4o-2024-08-06",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.1
)

# Initialize Weaviate client
try:
    weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.environ["WEAVIATE_URL"],
        auth_credentials=Auth.api_key(os.environ["WEAVIATE_API_KEY"]),
        headers={'X-OpenAI-Api-key': os.environ["OPENAI_API_KEY"]}
    )
    print("Connected to Weaviate:", weaviate_client.is_ready())
except Exception as e:
    print(f"Weaviate connection error: {e}")
    weaviate_client = None

@dataclass
class SimilarCase:
    id: str
    company: str
    description: str
    fine: int
    similarity: int
    explanation_of_similarity: str
    date: str
    authority: str

@dataclass
class PredictionResult:
    predicted_fine: int
    explanation_for_fine: str

class WorkflowState(TypedDict):
    case_description: str
    lawfulness_of_processing: str
    data_subject_rights_compliance: str
    risk_management_and_safeguards: str
    accountability_and_governance: str
    initial_candidates: List[Dict[str, Any]]
    similarity_analyses: List[Dict[str, Any]]
    similar_cases: List[SimilarCase]
    prediction_result: PredictionResult
    current_step: str
    error_message: str

def search_similar_cases(state: WorkflowState) -> WorkflowState:
    """
    Step 1: Search Weaviate for similar cases based on case description and classifications
    """
    try:
        if not weaviate_client or not weaviate_client.is_ready():
            raise Exception("Weaviate client not connected")
            
        collection = weaviate_client.collections.get("Precedent")
        
        # Create search query combining case description and classifications
        search_text = f"""
        Case Description: {state['case_description']}
        Lawfulness of Processing: {state['lawfulness_of_processing']}
        Data Subject Rights: {state['data_subject_rights_compliance']}
        Risk Management: {state['risk_management_and_safeguards']}
        Accountability: {state['accountability_and_governance']}
        """
        
        # Perform hybrid search on summary vector
        response = collection.query.hybrid(
            query=search_text,
            target_vector="summary_vector",  # Specify which vector to use
            limit=50,  # Get 50 candidates first
            return_metadata=MetadataQuery(distance=True),
            return_properties=[
                "precedent_id", "company", "violation", "summary", "fine_eur", 
                "date", "authority", "lawfulness_of_processing", 
                "data_subject_rights_compliance", "risk_management_and_safeguards",
                "accountability_and_governance"
            ]
        )
        
        # Group by precedent_id and select top 5 unique cases
        seen_precedents = set()
        candidates = []
        
        for obj in response.objects:
            precedent_id = obj.properties["precedent_id"]
            if precedent_id not in seen_precedents and len(candidates) < 5:
                seen_precedents.add(precedent_id)
                candidates.append({
                    "precedent_id": precedent_id,
                    "company": obj.properties["company"],
                    "violation": obj.properties["violation"],
                    "summary": obj.properties["summary"],
                    "fine_eur": obj.properties["fine_eur"],
                    "date": obj.properties["date"],
                    "authority": obj.properties["authority"],
                    "lawfulness_of_processing": obj.properties.get("lawfulness_of_processing"),
                    "data_subject_rights_compliance": obj.properties.get("data_subject_rights_compliance"),
                    "risk_management_and_safeguards": obj.properties.get("risk_management_and_safeguards"),
                    "accountability_and_governance": obj.properties.get("accountability_and_governance"),
                    "initial_distance": obj.metadata.distance if obj.metadata else None
                })
        
        state["initial_candidates"] = candidates
        state["current_step"] = "similarity_analysis"
        
    except Exception as e:
        # Enhanced mock data if Weaviate is not available (for testing)
        print(f"Warning in search_similar_cases: {str(e)}, using enhanced mock data")
        
        # Create more comprehensive mock data based on common GDPR breach scenarios
        mock_cases = [
            {
                "precedent_id": "mock_1",
                "company": "Meta Platforms Ireland",
                "violation": "Cross-border data transfers without adequate safeguards",
                "summary": "Meta was fined for transferring EU user data to the US without adequate protections under GDPR Article 44-49",
                "fine_eur": 1200000000,
                "date": "2023-05-22",
                "authority": "Irish DPC",
                "lawfulness_of_processing": "no_valid_basis",
                "data_subject_rights_compliance": "non_compliance",
                "risk_management_and_safeguards": "insufficient_protection",
                "accountability_and_governance": "not_accountable",
                "initial_distance": 0.3
            },
            {
                "precedent_id": "mock_2", 
                "company": "Amazon Europe Core",
                "violation": "Inappropriate data processing for advertising purposes without consent",
                "summary": "Amazon was fined for processing personal data for advertising without proper consent under GDPR Article 6",
                "fine_eur": 746000000,
                "date": "2021-07-30",
                "authority": "Luxembourg CNPD",
                "lawfulness_of_processing": "lawful_but_principle_violation",
                "data_subject_rights_compliance": "partial_compliance",
                "risk_management_and_safeguards": "reactive_only",
                "accountability_and_governance": "partially_accountable",
                "initial_distance": 0.4
            },
            {
                "precedent_id": "mock_3",
                "company": "WhatsApp Ireland Limited", 
                "violation": "Lack of transparency in data processing operations",
                "summary": "WhatsApp was fined for not providing sufficient transparency about how personal data is processed",
                "fine_eur": 225000000,
                "date": "2021-09-02",
                "authority": "Irish DPC",
                "lawfulness_of_processing": "lawful_but_principle_violation",
                "data_subject_rights_compliance": "partial_compliance",
                "risk_management_and_safeguards": "reactive_only", 
                "accountability_and_governance": "partially_accountable",
                "initial_distance": 0.5
            },
            {
                "precedent_id": "mock_4",
                "company": "Google LLC",
                "violation": "Processing personal data without legal basis for advertising",
                "summary": "Google was fined for processing user data for personalized advertising without valid legal basis",
                "fine_eur": 90000000,
                "date": "2022-01-06",
                "authority": "French CNIL",
                "lawfulness_of_processing": "no_valid_basis",
                "data_subject_rights_compliance": "non_compliance",
                "risk_management_and_safeguards": "insufficient_protection",
                "accountability_and_governance": "partially_accountable",
                "initial_distance": 0.45
            },
            {
                "precedent_id": "mock_5",
                "company": "TikTok Technology Limited",
                "violation": "Inadequate data protection measures for minors",
                "summary": "TikTok was fined for inadequate protection of children's personal data and lack of transparency",
                "fine_eur": 345000000,
                "date": "2023-09-15",
                "authority": "Irish DPC", 
                "lawfulness_of_processing": "lawful_but_principle_violation",
                "data_subject_rights_compliance": "partial_compliance",
                "risk_management_and_safeguards": "insufficient_protection",
                "accountability_and_governance": "partially_accountable",
                "initial_distance": 0.6
            }
        ]
        
        # Select most relevant mock cases based on query characteristics
        query_lower = state['case_description'].lower()
        query_classifications = [
            state['lawfulness_of_processing'],
            state['data_subject_rights_compliance'], 
            state['risk_management_and_safeguards'],
            state['accountability_and_governance']
        ]
        
        # Simple scoring based on keyword matching and classification similarity
        scored_cases = []
        for case in mock_cases:
            score = 0
            
            # Keyword matching
            case_text = f"{case['violation']} {case['summary']}".lower()
            common_keywords = ['data', 'processing', 'consent', 'transfer', 'breach', 'protection']
            for keyword in common_keywords:
                if keyword in query_lower and keyword in case_text:
                    score += 1
                    
            # Classification matching
            case_classifications = [
                case['lawfulness_of_processing'],
                case['data_subject_rights_compliance'],
                case['risk_management_and_safeguards'], 
                case['accountability_and_governance']
            ]
            
            matches = sum(1 for q, c in zip(query_classifications, case_classifications) if q == c)
            score += matches * 2
            
            scored_cases.append((score, case))
        
        # Sort by score and take top 5
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        state["initial_candidates"] = [case for _, case in scored_cases[:5]]
        state["current_step"] = "similarity_analysis"
    
    return state

def analyze_case_similarity(case_data: Dict[str, Any], query_case: WorkflowState) -> Dict[str, Any]:
    """
    Analyze similarity between a candidate case and the query case
    """
    try:
        # Get detailed chunks for this precedent case
        case_chunks = []
        
        if weaviate_client and weaviate_client.is_ready():
            collection = weaviate_client.collections.get("Precedent")
            
            # Use hybrid search to find similar chunks for this precedent
            chunks_response = collection.query.hybrid(
                query=query_case["case_description"],
                target_vector="chunk_vector",  # Target the chunk vector field
                where={
                    "path": ["precedent_id"],
                    "operator": "Equal",
                    "valueText": case_data["precedent_id"]
                },
                limit=10,
                return_properties=["chunk", "page"],
                return_metadata=MetadataQuery(distance=True)
            )
            
            # Combine chunks for analysis
            case_chunks = [obj.properties["chunk"] for obj in chunks_response.objects]
        
        # Use summary if no chunks available
        if not case_chunks:
            case_chunks = [case_data.get("summary", "No additional details available")]
            
        combined_chunks = "\n\n".join(case_chunks[:5])  # Use top 5 chunks
        
        # Create similarity analysis prompt
        similarity_prompt = f"""
        You are an expert legal analyst specializing in GDPR breach impact assessment.
        
        QUERY CASE:
        Description: {query_case['case_description']}
        Classifications:
        - Lawfulness of Processing: {query_case['lawfulness_of_processing']}
        - Data Subject Rights: {query_case['data_subject_rights_compliance']}
        - Risk Management: {query_case['risk_management_and_safeguards']}
        - Accountability: {query_case['accountability_and_governance']}
        
        PRECEDENT CASE:
        Company: {case_data['company']}
        Violation: {case_data['violation']}
        Summary: {case_data['summary']}
        Fine: €{case_data['fine_eur']:,}
        Date: {case_data['date']}
        Authority: {case_data['authority']}
        Classifications:
        - Lawfulness of Processing: {case_data.get('lawfulness_of_processing', 'N/A')}
        - Data Subject Rights: {case_data.get('data_subject_rights_compliance', 'N/A')}
        - Risk Management: {case_data.get('risk_management_and_safeguards', 'N/A')}
        - Accountability: {case_data.get('accountability_and_governance', 'N/A')}
        
        DETAILED CASE CONTENT:
        {combined_chunks}
        
        Please analyze the similarity between these two cases and provide:
        1. A similarity score from 0-100 (100 being identical)
        2. A detailed explanation of why they are similar or different
        
        Focus on:
        - Type of violation and circumstances
        - GDPR articles involved
        - Company size and sector similarities
        - Regulatory authority approach
        - Severity and impact factors
        
        Format your response as:
        SIMILARITY_SCORE: [score]
        EXPLANATION: [detailed explanation]
        """
        
        response = llm.invoke([HumanMessage(content=similarity_prompt)])
        content = response.content
        
        # Parse response
        lines = content.split('\n')
        similarity_score = 0
        explanation = ""
        
        for line in lines:
            if line.startswith('SIMILARITY_SCORE:'):
                try:
                    similarity_score = int(line.split(':')[1].strip())
                except:
                    similarity_score = 50  # Default if parsing fails
            elif line.startswith('EXPLANATION:'):
                explanation = line.split(':', 1)[1].strip()
            elif explanation and not line.startswith('SIMILARITY_SCORE:'):
                explanation += " " + line.strip()
        
        return {
            **case_data,
            "similarity_score": similarity_score,
            "explanation_of_similarity": explanation,
            "chunks_analyzed": len(case_chunks)
        }
        
    except Exception as e:
        # Enhanced fallback for similarity analysis errors
        print(f"Error in analyze_case_similarity: {str(e)}")
        
        # Calculate a basic similarity score based on classification matching
        query_classifications = [
            query_case['lawfulness_of_processing'],
            query_case['data_subject_rights_compliance'], 
            query_case['risk_management_and_safeguards'],
            query_case['accountability_and_governance']
        ]
        
        case_classifications = [
            case_data.get('lawfulness_of_processing'),
            case_data.get('data_subject_rights_compliance'),
            case_data.get('risk_management_and_safeguards'),
            case_data.get('accountability_and_governance')
        ]
        
        matches = sum(1 for q, c in zip(query_classifications, case_classifications) if q == c and q is not None and c is not None)
        similarity_score = min(20 + (matches * 15), 85)  # Base 20% + 15% per match, max 85%
        
        # Create a basic explanation
        explanation = f"Similarity based on {matches} matching GDPR classification criteria out of 4 total dimensions."
        if matches >= 3:
            explanation += " High similarity in regulatory violations and compliance factors."
        elif matches >= 2:
            explanation += " Moderate similarity in breach characteristics and compliance issues."
        else:
            explanation += " Limited similarity, but both involve GDPR violations with comparable regulatory response."
            
        return {
            **case_data,
            "similarity_score": similarity_score,
            "explanation_of_similarity": explanation,
            "chunks_analyzed": 0
        }

def similarity_analysis_step(state: WorkflowState) -> WorkflowState:
    """
    Step 2: Analyze similarity for each of the top 5 candidate cases
    """
    try:
        similarity_analyses = []
        
        for case_data in state["initial_candidates"]:
            analysis = analyze_case_similarity(case_data, state)
            similarity_analyses.append(analysis)
        
        # Sort by similarity score and take top 5
        similarity_analyses.sort(key=lambda x: x["similarity_score"], reverse=True)
        state["similarity_analyses"] = similarity_analyses[:5]
        state["current_step"] = "combine_results"
        
    except Exception as e:
        state["error_message"] = f"Error in similarity_analysis_step: {str(e)}"
        state["current_step"] = "error"
    
    return state

def combine_results_step(state: WorkflowState) -> WorkflowState:
    """
    Step 3: Combine similarity analyses and predict fine
    """
    try:
        # Convert analyses to SimilarCase format
        similar_cases = []
        for analysis in state["similarity_analyses"]:
            similar_case = SimilarCase(
                id=analysis["precedent_id"],
                company=analysis["company"],
                description=analysis["violation"],
                fine=analysis["fine_eur"],
                similarity=analysis["similarity_score"],
                explanation_of_similarity=analysis["explanation_of_similarity"],
                date=analysis["date"],
                authority=analysis["authority"]
            )
            similar_cases.append(similar_case)
        
        state["similar_cases"] = similar_cases
        
        # Create prediction prompt
        cases_summary = "\n".join([
            f"Case {i+1}: {case.company} - €{case.fine:,} (Similarity: {case.similarity}%)"
            for i, case in enumerate(similar_cases)
        ])
        
        prediction_prompt = f"""
        You are an expert GDPR legal analyst tasked with predicting the financial impact of a data breach.
        
        QUERY CASE:
        Description: {state['case_description']}
        Classifications:
        - Lawfulness of Processing: {state['lawfulness_of_processing']}
        - Data Subject Rights: {state['data_subject_rights_compliance']}
        - Risk Management: {state['risk_management_and_safeguards']}
        - Accountability: {state['accountability_and_governance']}
        
        SIMILAR PRECEDENT CASES:
        {cases_summary}
        
        DETAILED CASE ANALYSES:
        {chr(10).join([f"Case {i+1} ({case.company}): {case.explanation_of_similarity}" for i, case in enumerate(similar_cases)])}
        
        Based on these similar cases and their similarity scores, predict the likely fine amount in EUR.
        
        Consider:
        1. Weighted average based on similarity scores
        2. Regulatory trends and inflation
        3. Specific aggravating or mitigating factors
        4. Authority enforcement patterns
        
        Provide:
        1. A predicted fine amount in EUR (integer)
        2. A detailed explanation of your reasoning
        
        Format as:
        PREDICTED_FINE: [amount]
        EXPLANATION: [detailed reasoning]
        """
        
        response = llm.invoke([HumanMessage(content=prediction_prompt)])
        content = response.content
        
        # Parse response
        lines = content.split('\n')
        predicted_fine = 0
        explanation = ""
        
        for line in lines:
            if line.startswith('PREDICTED_FINE:'):
                try:
                    fine_str = line.split(':')[1].strip().replace(',', '').replace('€', '')
                    predicted_fine = int(fine_str)
                except:
                    # Fallback to weighted average
                    if similar_cases:
                        weighted_sum = sum(case.fine * (case.similarity / 100) for case in similar_cases)
                        predicted_fine = int(weighted_sum / len(similar_cases))
                    else:
                        predicted_fine = 1000000  # Default 1M EUR
            elif line.startswith('EXPLANATION:'):
                explanation = line.split(':', 1)[1].strip()
            elif explanation and not line.startswith('PREDICTED_FINE:'):
                explanation += " " + line.strip()
        
        state["prediction_result"] = PredictionResult(
            predicted_fine=predicted_fine,
            explanation_for_fine=explanation
        )
        state["current_step"] = "completed"
        
    except Exception as e:
        state["error_message"] = f"Error in combine_results_step: {str(e)}"
        state["current_step"] = "error"
    
    return state

def should_continue(state: WorkflowState) -> str:
    """Router function to determine next step"""
    current_step = state.get("current_step", "search")
    
    if current_step == "error":
        return END
    elif current_step == "similarity_analysis":
        return "similarity_analysis"
    elif current_step == "combine_results":
        return "combine_results"
    elif current_step == "completed":
        return END
    else:
        return "search"

# Create the workflow graph
def create_breach_impact_workflow():
    """Create and return the LangGraph workflow"""
    
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("search", search_similar_cases)
    workflow.add_node("similarity_analysis", similarity_analysis_step)
    workflow.add_node("combine_results", combine_results_step)
    
    # Add edges
    workflow.set_entry_point("search")
    workflow.add_conditional_edges(
        "search",
        should_continue,
        {
            "similarity_analysis": "similarity_analysis",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "similarity_analysis", 
        should_continue,
        {
            "combine_results": "combine_results",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "combine_results",
        should_continue,
        {
            END: END
        }
    )
    
    # Add memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

# Convenience function to run the workflow
async def predict_breach_impact(
    case_description: str,
    lawfulness_of_processing: str,
    data_subject_rights_compliance: str,
    risk_management_and_safeguards: str,
    accountability_and_governance: str
) -> Dict[str, Any]:
    """
    Run the breach impact prediction workflow
    
    Args:
        case_description: Description of the breach case
        lawfulness_of_processing: Classification for lawfulness
        data_subject_rights_compliance: Classification for data subject rights
        risk_management_and_safeguards: Classification for risk management
        accountability_and_governance: Classification for accountability
    
    Returns:
        Dictionary containing similar_cases and prediction_result
    """
    
    workflow = create_breach_impact_workflow()
    
    initial_state = WorkflowState(
        case_description=case_description,
        lawfulness_of_processing=lawfulness_of_processing,
        data_subject_rights_compliance=data_subject_rights_compliance,
        risk_management_and_safeguards=risk_management_and_safeguards,
        accountability_and_governance=accountability_and_governance,
        initial_candidates=[],
        similarity_analyses=[],
        similar_cases=[],
        prediction_result=None,
        current_step="search",
        error_message=""
    )
    
    # Run the workflow
    config = {"configurable": {"thread_id": f"breach_prediction_{datetime.now().isoformat()}"}}
    
    try:
        final_state = None
        final_node = None
        
        for chunk in workflow.stream(initial_state, config):
            final_state = chunk
            final_node = list(chunk.keys())[0]  # Get the node name
        
        if final_state and final_node:
            # Extract the actual state from the final node
            result_state = final_state[final_node]
            
            # Check if we have an error
            if result_state.get("error_message"):
                return {
                    "error": result_state["error_message"],
                    "similar_cases": [],
                    "prediction_result": {
                        "predicted_fine": 1000000,
                        "explanation_for_fine": f"Error in prediction: {result_state['error_message']}"
                    }
                }
            
            # Check if prediction_result exists and is valid
            if not result_state.get("prediction_result"):
                return {
                    "error": "Prediction result not generated",
                    "similar_cases": [],
                    "prediction_result": {
                        "predicted_fine": 1000000,
                        "explanation_for_fine": "Error: Prediction result not generated"
                    }
                }
            
            return {
                "similar_cases": [
                    {
                        "id": case.id,
                        "company": case.company,
                        "description": case.description,
                        "fine": case.fine,
                        "similarity": case.similarity,
                        "explanation_of_similarity": case.explanation_of_similarity,
                        "date": case.date,
                        "authority": case.authority
                    } for case in result_state["similar_cases"]
                ],
                "prediction_result": {
                    "predicted_fine": result_state["prediction_result"].predicted_fine,
                    "explanation_for_fine": result_state["prediction_result"].explanation_for_fine
                }
            }
        else:
            return {
                "error": "Workflow execution failed - no final state",
                "similar_cases": [],
                "prediction_result": {
                    "predicted_fine": 1000000,
                    "explanation_for_fine": "Error: Workflow execution failed"
                }
            }
            
    except Exception as e:
        return {
            "error": f"Workflow execution error: {str(e)}",
            "similar_cases": [],
            "prediction_result": {
                "predicted_fine": 1000000,
                "explanation_for_fine": f"Error in prediction: {str(e)}"
            }
        }

# Test function
def test_workflow():
    """Test the workflow with a sample case"""
    
    sample_case = {
        "case_description": "A healthcare company failed to implement proper access controls, resulting in unauthorized access to patient medical records by former employees. The breach affected 50,000 patients and included sensitive medical information.",
        "lawfulness_of_processing": "no_valid_basis",
        "data_subject_rights_compliance": "non_compliance", 
        "risk_management_and_safeguards": "insufficient_protection",
        "accountability_and_governance": "not_accountable"
    }
    
    # Run the workflow
    result = asyncio.run(predict_breach_impact(**sample_case))
    
    print("=== BREACH IMPACT PREDICTION RESULTS ===")
    print(f"\nCase: {sample_case['case_description'][:100]}...")
    print(f"\nPredicted Fine: €{result['prediction_result']['predicted_fine']:,}")
    print(f"Explanation: {result['prediction_result']['explanation_for_fine']}")
    
    print(f"\nSimilar Cases Found: {len(result['similar_cases'])}")
    for i, case in enumerate(result['similar_cases'], 1):
        print(f"\n{i}. {case['company']}")
        print(f"   Fine: €{case['fine']:,}")
        print(f"   Similarity: {case['similarity']}%")
        print(f"   Description: {case['description'][:100]}...")

if __name__ == "__main__":
    test_workflow()
