#!/usr/bin/env python3
"""
Detailed test to verify exact iteration counting and classification trigger.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def parse_sse_stream(response):
    conversation_id = None
    messages = []
    classification = None
    
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
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

def test_exact_iteration_trigger():
    print("🔍 Testing exact iteration trigger point...")
    
    # Start conversation
    response = requests.post(f"{BASE_URL}/api/start-case-gathering", 
                           json={"initial_description": "We had a data breach involving personal data."}, 
                           stream=True)
    
    conversation_id, message, classification = parse_sse_stream(response)
    print(f"INITIAL: Started conversation")
    print(f"Classification: {'✅ YES' if classification else '❌ NO'}")
    print(f"Agent response length: {len(message)} chars")
    print()
    
    if not conversation_id:
        return
    
    # Test each iteration explicitly
    responses = [
        "The breach involved customer email addresses and phone numbers.",
        "It happened due to a misconfigured database that was publicly accessible.",
        "We had basic security measures but they weren't adequate for this situation.",
        "We have some data protection policies and we notified customers."
    ]
    
    for i, user_msg in enumerate(responses, 1):
        print(f"ITERATION {i}: Sending user message")
        print(f"User: {user_msg}")
        
        continue_response = requests.post(f"{BASE_URL}/api/continue-case-gathering",
                                        json={
                                            "conversation_id": conversation_id,
                                            "user_response": user_msg
                                        },
                                        stream=True)
        
        if continue_response.status_code == 200:
            _, agent_message, classification = parse_sse_stream(continue_response)
            print(f"Classification: {'✅ YES' if classification else '❌ NO'}")
            print(f"Agent response: {agent_message[:100]}...")
            
            if classification:
                print(f"\n🎉 CLASSIFICATION TRIGGERED ON ITERATION {i}!")
                print(f"Classification details: {json.dumps(classification, indent=2)}")
                break
        else:
            print(f"❌ Error: {continue_response.status_code}")
            break
            
        print()

if __name__ == "__main__":
    print("🧪 Testing exact iteration trigger behavior...")
    time.sleep(1)
    
    try:
        test_exact_iteration_trigger()
        print("\n✅ Detailed test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
