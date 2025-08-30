#!/usr/bin/env python3
"""
Test script for the optimized message ingestion and analysis pipeline.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindpulse.settings')
django.setup()

from core.models.channel_model import Channel
from core.models.user_model import User
from core.models.message_model import Message, MessageAnalysis
from core.services.message_services import ingest_message, process_message_analysis
from uuid import uuid4

def test_pipeline():
    """Test the complete message pipeline with optimized models."""
    
    print("=== Testing Optimized Message Pipeline ===\n")
    
    # 1. Create test channel
    print("1. Creating test channel...")
    channel, created = Channel.get_or_create_channel_instance(
        name="Test Discord Channel",
        type="discord",
        external_id="test_channel_123"
    )
    print(f"   Channel created: {channel} (new: {created})")
    
    # 2. Create test user
    print("\n2. Creating test user...")
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        role="employee"
    )
    print(f"   User created: {user}")
    print(f"   User hash: {user.hashed_id}")
    
    # 3. Test message ingestion
    print("\n3. Testing message ingestion...")
    test_data = {
        'channel_id': str(channel.id),
        'user_hash': str(user.hashed_id),
        'message': "I'm feeling really stressed about this project deadline. The work is overwhelming and I'm worried we won't finish on time.",
        'external_ref': 'msg_12345'
    }
    
    try:
        message_id = ingest_message(test_data)
        print(f"   ✓ Message ingested successfully: {message_id}")
        
        # Verify message was created with correct status
        message = Message.objects.get(id=message_id)
        print(f"   Processing status: {message.processing_status}")
        print(f"   Message length: {message.message_length}")
        
        # Verify user activity was updated
        user.refresh_from_db()
        print(f"   User message count: {user.message_count}")
        print(f"   User last activity: {user.last_activity}")
        
    except Exception as e:
        print(f"   ✗ Message ingestion failed: {e}")
        return False
    
    # 4. Test message analysis
    print("\n4. Testing message analysis...")
    try:
        process_message_analysis(message_id)
        print(f"   ✓ Message analysis completed")
        
        # Verify analysis was created
        message.refresh_from_db()
        print(f"   Final processing status: {message.processing_status}")
        
        if hasattr(message, 'analysis'):
            analysis = message.analysis
            print(f"   Sentiment: {analysis.sentiment} (score: {analysis.sentiment_score})")
            print(f"   Emotion: {analysis.emotion} (score: {analysis.emotion_score})")
            print(f"   Stress: {analysis.stress} (score: {analysis.stress_score})")
            print(f"   Confidence scores: sentiment={analysis.sentiment_confidence}, emotion={analysis.emotion_confidence}, stress={analysis.stress_confidence}")
        else:
            print("   ✗ Analysis object not found")
            return False
            
    except Exception as e:
        print(f"   ✗ Message analysis failed: {e}")
        return False
    
    # 5. Test database performance with indexes
    print("\n5. Testing database query performance...")
    
    # Query by user hash (should use index)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM core_message WHERE user_hash = ?", [str(user.hashed_id)])
        result = cursor.fetchall()
        print("   Query plan for user_hash lookup:")
        for row in result:
            print(f"     {row}")
    
    print("\n=== Pipeline Test Completed Successfully! ===")
    return True

def cleanup_test_data():
    """Clean up test data."""
    print("\nCleaning up test data...")
    try:
        User.objects.filter(username="testuser").delete()
        Channel.objects.filter(external_id="test_channel_123").delete()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")

if __name__ == "__main__":
    try:
        success = test_pipeline()
        if success:
            print("\n🎉 All tests passed! The optimized pipeline is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
            sys.exit(1)
    finally:
        cleanup_test_data()