#!/usr/bin/env python3
"""
Comprehensive test for complete GDPR case classification flow.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def parse_sse_stream(response):
    """Parse Server-Sent Events stream"""
    conversation_id = None
    messages = []
    classification = None
    
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])  # Remove 'data: ' prefix
                if data.get('type') == 'conversation_id':
                    conversation_id = data.get('data')
                elif data.get('type') == 'message':
                    messages.append(data.get('data'))
                elif data.get('type') == 'classification_complete':
                    classification = data.get('data')
                elif data.get('type') == 'stream_end':
                    break
            except json.JSONDecodeError:
                continue
                
    return conversation_id, ''.join(messages), classification

def complete_classification_flow():
    """Test a complete GDPR classification flow"""
    print("🧪 Testing complete GDPR case classification flow...")
    
    # Start with a detailed case description
    initial_case = """We had a data breach where an employee accidentally sent an email containing customer information 
    to an external marketing company. The email included names, addresses, phone numbers, and purchase history of 200 customers. 
    We were processing this data under legitimate interest for marketing purposes. We discovered the breach when the external 
    company contacted us about receiving the wrong email. We had basic email encryption but no DLP system in place. 
    We notified affected customers within 72 hours and have documented data protection policies."""
    
    print(f"Starting case: {initial_case[:100]}...")
    
    # Step 1: Start conversation
    response = requests.post(f"{BASE_URL}/api/start-case-gathering", 
                           json={"initial_description": initial_case},
                           stream=True)
    
    if response.status_code == 200:
        conversation_id, message, classification = parse_sse_stream(response)
        print(f"✅ Started conversation: {conversation_id}")
        print(f"Agent: {message}")
        
        if classification:
            print("🎉 Classification completed immediately!")
            print(f"Classification: {json.dumps(classification, indent=2)}")
            return
        
        # Step 2: Provide additional information to trigger classification
        additional_info = """We had a legal basis under legitimate interest for marketing. The data subjects were existing customers. 
        We have a data protection officer and documented procedures. The breach was human error, not a technical failure. 
        We responded immediately by contacting the external company to delete the data, notified customers, and reported to the supervisory authority."""
        
        print(f"\nProviding additional info to complete classification...")
        continue_response = requests.post(f"{BASE_URL}/api/continue-case-gathering",
                                        json={
                                            "conversation_id": conversation_id,
                                            "user_response": additional_info
                                        },
                                        stream=True)
        
        if continue_response.status_code == 200:
            _, continue_message, continue_classification = parse_sse_stream(continue_response)
            print(f"Agent: {continue_message}")
            
            if continue_classification:
                print("🎉 Classification completed!")
                print(f"Final Classification: {json.dumps(continue_classification, indent=2)}")
            else:
                print("ℹ️ Classification not yet complete, may need more interaction")
                
                # Step 3: Check final status
                status_response = requests.get(f"{BASE_URL}/api/case-gathering/{conversation_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"Final status: {json.dumps(status, indent=2)}")
        else:
            print(f"❌ Failed to continue: {continue_response.status_code}")
    else:
        print(f"❌ Failed to start: {response.status_code}")

if __name__ == "__main__":
    print("🧪 Starting comprehensive GDPR classification test...")
    time.sleep(1)
    
    try:
        complete_classification_flow()
        print("\n✅ Comprehensive test completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
