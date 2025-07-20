#!/usr/bin/env python3
"""
Direct test to force classification with complete information.
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
    errors = []
    
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
                elif data.get('type') == 'error':
                    errors.append(data.get('data'))
                elif data.get('type') == 'stream_end':
                    break
            except json.JSONDecodeError:
                continue
                
    return conversation_id, ''.join(messages), classification, errors

def force_classification_test():
    """Force classification with extremely detailed case"""
    print("🧪 Testing forced classification with complete information...")
    
    # Extremely detailed case that should trigger immediate classification
    complete_case = """Please classify this GDPR breach case:
    
    CASE DETAILS:
    - Data Type: Customer names, addresses, phone numbers, purchase history (200 customers)
    - Breach Method: Employee accidentally emailed data to external marketing company
    - Legal Basis: Legitimate interest for marketing (properly documented with assessment)
    - Discovery: External company contacted us about wrong email
    - Notification: Customers notified within 72 hours, supervisory authority reported
    - Security: Basic email encryption present, but NO DLP system
    - Response: Immediate - contacted external company to delete data, full investigation conducted
    - Policies: Full documented data protection policies, dedicated DPO appointed
    - Training: Regular staff training on data protection
    - Incident Type: Human error (not technical failure or malicious attack)
    
    Please immediately classify this case across all four GDPR dimensions using your finalize_classification function."""
    
    print(f"Testing with complete case details...")
    
    response = requests.post(f"{BASE_URL}/api/start-case-gathering", 
                           json={"initial_description": complete_case},
                           stream=True)
    
    if response.status_code == 200:
        conversation_id, message, classification, errors = parse_sse_stream(response)
        print(f"✅ Conversation ID: {conversation_id}")
        print(f"Agent Response: {message}")
        
        if classification:
            print("🎉 SUCCESS! Classification completed!")
            print(f"Classification: {json.dumps(classification, indent=2)}")
        else:
            print("❌ Classification not completed")
            
        if errors:
            print(f"Errors: {errors}")
            
        # Follow up with explicit instruction
        if not classification:
            print("\nForcing classification with direct instruction...")
            force_response = requests.post(f"{BASE_URL}/api/continue-case-gathering",
                                         json={
                                             "conversation_id": conversation_id,
                                             "user_response": "Based on the information I provided, please immediately use your finalize_classification function to classify this case. You have all the information needed: legal basis (legitimate interest), notification compliance (within 72 hours), security measures (basic encryption but no DLP), and governance (DPO and documented policies). Please classify now."
                                         },
                                         stream=True)
            
            if force_response.status_code == 200:
                _, force_message, force_classification, force_errors = parse_sse_stream(force_response)
                print(f"Force Response: {force_message}")
                
                if force_classification:
                    print("🎉 FORCED CLASSIFICATION SUCCESS!")
                    print(f"Classification: {json.dumps(force_classification, indent=2)}")
                else:
                    print("❌ Even forced classification failed")
                    
                if force_errors:
                    print(f"Force Errors: {force_errors}")
    else:
        print(f"❌ Failed to start: {response.status_code}")

if __name__ == "__main__":
    print("🧪 Starting forced classification test...")
    time.sleep(1)
    
    try:
        force_classification_test()
        print("\n✅ Forced classification test completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
