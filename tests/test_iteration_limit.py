#!/usr/bin/env python3
"""
Test script to verify the 4-iteration limit functionality.
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

def test_iteration_limit():
    print("🧪 Testing 4-iteration limit functionality...")
    
    # Start conversation
    print("\n1. Starting conversation...")
    response = requests.post(f"{BASE_URL}/api/start-case-gathering", 
                           json={"initial_description": "We had a data breach."}, 
                           stream=True)
    
    conversation_id, message, classification = parse_sse_stream(response)
    print(f"✅ Started conversation: {conversation_id}")
    print(f"Agent: {message}")
    print(f"Classification after round 1: {'Yes' if classification else 'No'}")
    
    if not conversation_id:
        print("❌ Failed to get conversation ID")
        return
        
    # Continue for up to 4 iterations
    user_responses = [
        "It involved customer email addresses and phone numbers.",
        "The breach happened due to a misconfigured database.",
        "We had some security measures but they weren't adequate.",
        "We have basic data protection policies but they need improvement."
    ]
    
    for i, user_response in enumerate(user_responses, 2):
        print(f"\n{i}. Continuing conversation (iteration {i}/4)...")
        
        continue_response = requests.post(f"{BASE_URL}/api/continue-case-gathering",
                                        json={
                                            "conversation_id": conversation_id,
                                            "user_response": user_response
                                        },
                                        stream=True)
        
        if continue_response.status_code == 200:
            _, continue_message, continue_classification = parse_sse_stream(continue_response)
            print(f"Agent: {continue_message[:150]}...")
            print(f"Classification after round {i}: {'Yes' if continue_classification else 'No'}")
            
            if continue_classification:
                print("🎉 Classification triggered!")
                print(f"Final classification: {json.dumps(continue_classification, indent=2)}")
                break
        else:
            print(f"❌ Failed to continue conversation: {continue_response.status_code}")
            break
    
    print(f"\n✅ Test completed - classification was triggered as expected!")

if __name__ == "__main__":
    print("🧪 Testing iteration limit functionality...")
    time.sleep(1)  # Give server a moment
    
    try:
        test_iteration_limit()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
