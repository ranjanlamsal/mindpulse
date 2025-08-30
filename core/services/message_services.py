from django.db import transaction
from core.exceptions import (
    MindPulseException, InvalidChannelError, MessageProcessingError
)
from core.models.message_model import Message, MessageAnalysis
from core.models.channel_model import Channel
from core.models.user_model import User
from transformers import pipeline
import logging
from core.services.model_services import (
    detect_stress,
    detect_emotion,
    detect_sentiment
)
from django.utils import timezone


logger = logging.getLogger(__name__)


def ingest_message(data):
    """Ingest a single message and trigger analysis."""
    try:
        with transaction.atomic():
            # Validate channel and user
            try:
                channel = Channel.objects.get(id=data['channel_id'], is_active=True)
                print(channel)
            except Channel.DoesNotExist:
                raise InvalidChannelError(f"Invalid or inactive channel: {data['channel_id']}")

            # Create message with processing status
            message = Message.objects.create(
                channel=channel,
                external_ref=data.get('external_ref'),
                user_hash=data['user_hash'],
                message=data['message'],
                processing_status='pending'
            )
            
            # Update user activity tracking
            update_user_activity(data['user_hash'])
            
            return message.id
    except Exception as e:
        logger.error(f"Message ingestion failed: {e}")
        raise MindPulseException(f"Failed to ingest message: {str(e)}")

def process_message_analysis(message_id):
    """Process message with NLP models and store analysis."""
    try:
        message = Message.objects.get(id=message_id)
        
        # Update processing status
        message.processing_status = 'processing'
        message.save(update_fields=['processing_status'])
        
        with transaction.atomic():
            # Run NLP models
            sentiment, sentiment_score = detect_sentiment(message.message)
            emotion, emotion_score = detect_emotion(message.message)
            stress_label, stress_score = detect_stress(message.message)

            # Create analysis with confidence scores
            MessageAnalysis.objects.create(
                message=message,
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                emotion=emotion,
                emotion_score=emotion_score,
                stress=stress_label,
                stress_score=stress_score,
                sentiment_confidence=1.0,  # Default confidence
                emotion_confidence=1.0,
                stress_confidence=1.0
            )
            
            # Mark message as completed
            message.processing_status = 'completed'
            message.save(update_fields=['processing_status'])
            
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found")
        raise MessageProcessingError(f"Message {message_id} not found")
    except Exception as e:
        logger.error(f"Error processing message {message_id}: {e}")
        # Mark message as failed
        try:
            message = Message.objects.get(id=message_id)
            message.processing_status = 'failed'
            message.save(update_fields=['processing_status'])
        except Message.DoesNotExist:
            pass
        raise MessageProcessingError(f"Failed to process message: {str(e)}")


def update_user_activity(user_hash):
    """Update user's last activity timestamp and message count."""
    try:
        user = User.objects.get(hashed_id=user_hash)
        user.last_activity = timezone.now()
        user.message_count = user.message_count + 1
        user.save(update_fields=['last_activity', 'message_count'])
    except User.DoesNotExist:
        logger.warning(f"User with hash {user_hash} not found for activity update")
    except Exception as e:
        logger.error(f"Failed to update user activity for {user_hash}: {e}")
    