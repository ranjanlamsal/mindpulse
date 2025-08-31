#!/usr/bin/env python3
"""Test script to check if models can be loaded properly"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindpulse.settings')
django.setup()

def test_models():
    try:
        print("Testing model loading...")
        
        # Test model accessors
        from core.accessors.model_accessors import stress_classifier, emotion_classifier, sentiment_classifier
        
        print("✓ Model accessors imported successfully")
        
        # Test each model with a simple message
        test_message = "I am feeling happy today"
        
        # Test sentiment
        print("Testing sentiment classifier...")
        sentiment_result = sentiment_classifier(test_message)
        print(f"✓ Sentiment result: {sentiment_result}")
        
        # Test emotion
        print("Testing emotion classifier...")
        emotion_result = emotion_classifier(test_message)
        print(f"✓ Emotion result: {emotion_result}")
        
        # Test stress
        print("Testing stress classifier...")
        stress_result = stress_classifier(test_message)
        print(f"✓ Stress result: {stress_result}")
        
        print("\n✓ All models loaded and working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_services():
    try:
        print("\nTesting model services...")
        
        from core.services.model_services import detect_sentiment, detect_emotion, detect_stress
        
        test_message = "I am feeling happy today"
        
        # Test services
        sentiment, sentiment_score = detect_sentiment(test_message)
        print(f"✓ Sentiment service: {sentiment} (score: {sentiment_score})")
        
        emotion, emotion_score = detect_emotion(test_message)  
        print(f"✓ Emotion service: {emotion} (score: {emotion_score})")
        
        stress, stress_score = detect_stress(test_message)
        print(f"✓ Stress service: {stress} (score: {stress_score})")
        
        print("\n✓ All model services working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Model services test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_message_analysis_task():
    try:
        print("\nTesting message analysis task...")
        
        # Create a test message
        from core.models.message_model import Message
        from core.models.channel_model import Channel
        from core.models.user_model import User
        
        # Get or create test objects
        channel, _ = Channel.objects.get_or_create(
            name="test_channel",
            type="discord",
            external_id="test_123",
            defaults={"is_active": True}
        )
        
        import uuid
        test_user_uuid = uuid.uuid4()
        
        user, _ = User.objects.get_or_create(
            username="test_user",
            defaults={
                "hashed_id": test_user_uuid,
                "email": "test@example.com",
                "is_active": True
            }
        )
        
        message = Message.objects.create(
            message="I am feeling happy today",
            user_hash=user.hashed_id,
            channel=channel,
            external_ref="test_msg_123"
        )
        
        print(f"✓ Test message created with ID: {message.id}")
        
        # Test the task directly (not through Celery)
        from core.tasks.message_analysis_tasks import process_message_analysis
        
        result = process_message_analysis(message.id)
        print(f"✓ Task executed: {result}")
        
        # Check if analysis was created
        from core.models.message_model import MessageAnalysis
        analysis = MessageAnalysis.objects.filter(message=message).first()
        
        if analysis:
            print(f"✓ MessageAnalysis created: sentiment={analysis.sentiment}, emotion={analysis.emotion}, stress={analysis.stress}")
        else:
            print("✗ No MessageAnalysis object was created")
            
        print("\n✓ Message analysis task test completed!")
        return True
        
    except Exception as e:
        print(f"✗ Message analysis task test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting model and task tests...\n")
    
    models_ok = test_models()
    services_ok = test_model_services()
    task_ok = test_message_analysis_task()
    
    if models_ok and services_ok and task_ok:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)