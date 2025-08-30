from celery import shared_task
from core.models.message_model import Message, MessageAnalysis
from django.db import transaction
from transformers import pipeline
from core.services.model_services import (
    detect_stress,
    detect_emotion,
    detect_sentiment
)
import logging


logger = logging.getLogger(__name__)

@shared_task
def process_message_analysis(message_id):
    try:
        message = Message.objects.get(id=message_id)
        with transaction.atomic():
            # Run NLP models
            sentiment, sentiment_score = detect_sentiment(message.message)
            emotion, emotion_score = detect_emotion(message.message)
            stress_label, stress_score = detect_stress(message.message)

            # Create analysis
            MessageAnalysis.objects.create(
                message=message,
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                emotion=emotion,
                emotion_score=emotion_score,
                stress=stress_label,
                stress_score=stress_score
            )
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found")
    except Exception as e:
        logger.error(f"Error processing message {message_id}: {e}")
    