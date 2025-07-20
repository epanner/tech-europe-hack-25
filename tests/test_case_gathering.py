#!/usr/bin/env python3
"""
Test script for the OpenAI Agents SDK powered case gathering endpoints
"""

import requests
import json
import time

def test_start_case_gathering():
    """Test starting a new case gathering conversation"""
    url = "http://127.0.0.1:5000/api/start-case-gathering"
    
    payload = {
        "initial_description": "We had a data breach where customer email addresses were exposed due to a misconfigured database."
    }
    
    print("🚀 Testing /api/start-case-gathering endpoint...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        
        if response.status_code == 200:
            print("✅ Connection successful! Streaming response:")
            print("-" * 50)
            
            conversation_id = None
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        if data_str.strip():
                            try:
                                data = json.loads(data_str)
                                if data.get('type') == 'conversation_id':
                                    conversation_id = data.get('data')
                                    print(f"📝 Conversation ID: {conversation_id}")
                                elif data.get('type') == 'message':
                                    print(data.get('data', ''), end='')
                                elif data.get('type') == 'classification_complete':
                                    print(f"\n✅ Classification complete: {json.dumps(data.get('data'), indent=2)}")
                                elif data.get('type') == 'stream_end':
                                    print("\n🏁 Stream ended")
                                    break
                                elif data.get('type') == 'error':
                                    print(f"\n❌ Error: {data.get('data')}")
                                    break
                            except json.JSONDecodeError as e:
                                print(f"⚠️  JSON decode error: {e} for data: {data_str}")
            
            return conversation_id
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_continue_conversation(conversation_id: str):
    """Test continuing a conversation"""
    if not conversation_id:
        print("⏭️  Skipping continue conversation test (no conversation ID)")
        return
        
    url = "http://127.0.0.1:5000/api/continue-case-gathering"
    
    payload = {
        "conversation_id": conversation_id,
        "user_response": "The breach affected about 1000 customers. We discovered it when a customer contacted us about receiving spam emails. We had basic security measures but no encryption on that particular database."
    }
    
    print(f"\n🔄 Testing /api/continue-case-gathering endpoint...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        
        if response.status_code == 200:
            print("✅ Connection successful! Streaming response:")
            print("-" * 50)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str.strip():
                            try:
                                data = json.loads(data_str)
                                if data.get('type') == 'message':
                                    print(data.get('data', ''), end='')
                                elif data.get('type') == 'classification_complete':
                                    print(f"\n✅ Classification complete: {json.dumps(data.get('data'), indent=2)}")
                                elif data.get('type') == 'stream_end':
                                    print("\n🏁 Stream ended")
                                    break
                                elif data.get('type') == 'error':
                                    print(f"\n❌ Error: {data.get('data')}")
                                    break
                            except json.JSONDecodeError as e:
                                print(f"⚠️  JSON decode error: {e} for data: {data_str}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing OpenAI Agents SDK Case Gathering Endpoints")
    print("=" * 60)
    
    # Test starting a conversation
    conversation_id = test_start_case_gathering()
    
    # Wait a bit before continuing
    time.sleep(2)
    
    # Test continuing the conversation
    test_continue_conversation(conversation_id)
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")

if __name__ == "__main__":
    main()
