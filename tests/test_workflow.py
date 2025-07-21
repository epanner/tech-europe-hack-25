"""
Test script for the Breach Impact Prediction Workflow

This script tests both the LangGraph workflow and the FastAPI integration
"""

import asyncio
import requests
import json
from backend.breach_impact_workflow import test_workflow
from backend.breach_impact_api import app

def test_langgraph_workflow():
    """Test the LangGraph workflow directly"""
    print("=" * 50)
    print("TESTING LANGGRAPH WORKFLOW")
    print("=" * 50)
    
    try:
        test_workflow()
        print("\n✅ LangGraph workflow test completed successfully!")
    except Exception as e:
        print(f"\n❌ LangGraph workflow test failed: {e}")

def test_fastapi_integration():
    """Test the FastAPI integration"""
    print("\n" + "=" * 50)
    print("TESTING FASTAPI INTEGRATION")
    print("=" * 50)
    
    # Test data
    test_case = {
        "case_description": "A fintech company experienced a data breach due to inadequate encryption of customer financial data. Personal information of 100,000 customers including bank account details was exposed through an unsecured API endpoint.",
        "lawfulness_of_processing": "no_valid_basis",
        "data_subject_rights_compliance": "non_compliance",
        "risk_management_and_safeguards": "insufficient_protection", 
        "accountability_and_governance": "not_accountable"
    }
    
    try:
        # Start the server in a separate process would be needed for a real test
        # For now, we'll just test the endpoint logic
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        print("✅ Health check passed")
        
        # Test classifications endpoint
        response = client.get("/classifications")
        assert response.status_code == 200
        print("✅ Classifications endpoint passed")
        
        # Test prediction endpoint
        response = client.post("/predict-breach-impact", json=test_case)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ FastAPI prediction endpoint test passed")
            print(f"   Predicted Fine: €{result['prediction_result']['predicted_fine']:,}")
            print(f"   Similar Cases Found: {len(result['similar_cases'])}")
        else:
            print(f"❌ FastAPI test failed with status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ FastAPI integration test failed: {e}")

def test_invalid_input():
    """Test API with invalid input"""
    print("\n" + "=" * 50)  
    print("TESTING INVALID INPUT HANDLING")
    print("=" * 50)
    
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test with invalid classification
        invalid_case = {
            "case_description": "Test case",
            "lawfulness_of_processing": "invalid_value",
            "data_subject_rights_compliance": "non_compliance",
            "risk_management_and_safeguards": "insufficient_protection",
            "accountability_and_governance": "not_accountable"
        }
        
        response = client.post("/predict-breach-impact", json=invalid_case)
        
        if response.status_code == 400:
            print("✅ Invalid input correctly rejected")
        else:
            print(f"❌ Invalid input should have been rejected but got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid input test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Breach Impact Prediction Workflow Tests")
    
    # Test LangGraph workflow
    test_langgraph_workflow()
    
    # Test FastAPI integration  
    test_fastapi_integration()
    
    # Test invalid input handling
    test_invalid_input()
    
    print("\n🎉 All tests completed!")
