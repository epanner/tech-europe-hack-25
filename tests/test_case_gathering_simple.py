#!/usr/bin/env python3
"""
Test script for the case gathering agent endpoints.
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

def test_case_gathering_endpoints():
    print("Testing case gathering endpoints...")
    
    # Test 1: Start a new case gathering conversation
    print("\n1. Starting new case gathering conversation...")
    response = requests.post(f"{BASE_URL}/api/start-case-gathering", 
                           json={"initial_description": "We had a data breach where employee records were accidentally emailed to the wrong person."},
                           stream=True)
    
    if response.status_code == 200:
        conversation_id, message, classification = parse_sse_stream(response)
        print(f"✅ Started conversation with ID: {conversation_id}")
        print(f"Agent response: {message[:100]}..." if len(message) > 100 else message)
        
        if conversation_id:
            # Test 2: Continue the conversation
            print("\n2. Continuing conversation...")
            continue_response = requests.post(f"{BASE_URL}/api/continue-case-gathering",
                                            json={
                                                "conversation_id": conversation_id,
                                                "user_response": "The data included names, addresses, and employee ID numbers of about 50 employees. We had a legal basis for processing under employment contract."
                                            },
                                            stream=True)
            
            if continue_response.status_code == 200:
                _, continue_message, continue_classification = parse_sse_stream(continue_response)
                print("✅ Successfully continued conversation")
                print(f"Agent response: {continue_message[:100]}..." if len(continue_message) > 100 else continue_message)
                if continue_classification:
                    print(f"Classification completed: {continue_classification}")
            else:
                print(f"❌ Failed to continue conversation: {continue_response.status_code}")
                print("Error:", continue_response.text)
                
            # Test 3: Get conversation status
            print("\n3. Getting conversation status...")
            status_response = requests.get(f"{BASE_URL}/api/case-gathering/{conversation_id}")
            
            if status_response.status_code == 200:
                print("✅ Got conversation status")
                status = status_response.json()
                print(f"Conversation complete: {status.get('conversation_complete', False)}")
                if status.get('classification'):
                    print(f"Classification available: {json.dumps(status.get('classification'), indent=2)}")
            else:
                print(f"❌ Failed to get conversation status: {status_response.status_code}")
                print("Error:", status_response.text)
        else:
            print("❌ No conversation ID received")
            
    else:
        print(f"❌ Failed to start conversation: {response.status_code}")
        print("Error:", response.text)

def test_streaming_endpoint():
    print("\n\nTesting streaming functionality...")
    
    # Test streaming response with a complete scenario
    try:
        response = requests.post(f"{BASE_URL}/api/start-case-gathering", 
                               json={"initial_description": "We had a ransomware attack that encrypted our customer database."}, 
                               stream=True)
        
        if response.status_code == 200:
            print("✅ Streaming response received")
            conversation_id, message, classification = parse_sse_stream(response)
            print(f"Conversation ID: {conversation_id}")
            print(f"Agent message: {message}")
            print(f"Classification: {'Complete' if classification else 'Pending'}")
        else:
            print(f"❌ Streaming failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Streaming test failed: {str(e)}")

if __name__ == "__main__":
    print("🧪 Starting case gathering endpoint tests...")
    
    # Give the server a moment to fully start up
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    try:
        test_case_gathering_endpoints()
        test_streaming_endpoint()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
