#!/usr/bin/env python3
"""Test script to test the API endpoint directly"""
import requests
import uuid
import json

def create_test_user():
    """Create a test user directly in the database"""
    import os
    import sys
    import django
    
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindpulse.settings')
    django.setup()
    
    from core.models.user_model import User
    
    try:
        user, created = User.objects.get_or_create(
            username="test_user_api",
            defaults={
                "email": "test_api@example.com",
                "is_active": True
            }
        )
        print(f"{'Created' if created else 'Found'} test user: {user.username} (ID: {user.hashed_id})")
        return user.username
    except Exception as e:
        print(f"Failed to create user: {e}")
        return None

def test_message_ingestion():
    """Test the message ingestion API endpoint"""
    
    # First, create a test user
    username = create_test_user()
    if not username:
        print("Failed to create test user, exiting...")
        return False
    
    # Create a channel
    channel_data = {
        "name": "test_channel",
        "type": "discord",
        "external_id": "test_channel_123"
    }
    
    print("Creating test channel...")
    channel_response = requests.post(
        "http://127.0.0.1:8000/api/channels/", 
        json=channel_data
    )
    
    print(f"Channel creation response: {channel_response.status_code}")
    print(f"Channel data: {channel_response.text}")
    
    if channel_response.status_code not in [200, 201]:
        print("Failed to create channel, exiting...")
        return False
    
    channel_info = channel_response.json()
    channel_id = channel_info.get('data', {}).get('id')
    
    if not channel_id:
        print("No channel ID returned, exiting...")
        return False
    
    # Create test message
    message_data = {
        "channel_id": channel_id,
        "username": username,
        "message": "I am feeling really happy today! This is a wonderful day.",
        "external_ref": f"test_msg_{uuid.uuid4()}"
    }
    
    print(f"\nSending test message...")
    print(f"Message data: {json.dumps(message_data, indent=2)}")
    
    # Send message to API
    message_response = requests.post(
        "http://127.0.0.1:8000/api/messages/", 
        json=message_data
    )
    
    print(f"\nMessage ingestion response: {message_response.status_code}")
    print(f"Response body: {message_response.text}")
    
    if message_response.status_code in [200, 201]:
        print("✅ Message sent successfully!")
        response_data = message_response.json()
        
        # Check if task was queued
        processed_messages = response_data.get('data', {}).get('processed_messages', [])
        if processed_messages:
            status = processed_messages[0].get('status')
            print(f"✅ Message status: {status}")
            
            if status == 'queued_for_analysis':
                print("✅ Message was queued for analysis - check Celery logs")
                return True
            else:
                print(f"❌ Unexpected status: {status}")
                return False
        else:
            print("❌ No processed messages in response")
            return False
    else:
        print(f"❌ Message ingestion failed: {message_response.text}")
        return False

if __name__ == "__main__":
    print("Testing message ingestion API...\n")
    
    success = test_message_ingestion()
    
    if success:
        print("\n✅ API test completed successfully!")
        print("Check the Celery worker logs to see if the task was processed.")
        print("Also check the database for MessageAnalysis objects.")
    else:
        print("\n❌ API test failed!")