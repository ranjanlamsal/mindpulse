from core.accessors.model_accessors import (
    stress_classifier,
    emotion_classifier,
    sentiment_classifier,
)
import logging
from core.exceptions import MessageProcessingError
from core.constants import (
    SENTIMENT_MAPPING,
    STRESS_MAPPING,
    EMOTION_MAPPING
)


logger = logging.getLogger(__name__)

def detect_stress(text):
    """Run stress detection model."""
    try:
        result = stress_classifier(text)[0]
        label = result['label']
        mapped_stress = STRESS_MAPPING.get(label)

        if mapped_stress is None:
            logger.warning(f"Unknown stress label: {label}. Defaulting to False.")
            mapped_stress = False
        return mapped_stress, result['score']
    except Exception as e:
        logger.error(f"Stress detection failed: {e}")
        raise MessageProcessingError(f"Stress detection failed: {str(e)}")

def detect_emotion(text):
    """Run emotion detection model."""
    try:
        result = emotion_classifier(text)[0]
        label = result['label']
        mapped_emotion = EMOTION_MAPPING.get(label)
        if mapped_emotion is None:
            logger.warning(f"Unknown emotion label: {label}. Defaulting to 'unknown'.")
            mapped_emotion = "unknown"
        return mapped_emotion, result['score']
    except Exception as e:
        logger.error(f"Emotion detection failed: {e}")
        raise MessageProcessingError(f"Emotion detection failed: {str(e)}")

def detect_sentiment(text):
    """Run sentiment detection model."""
    try:
        result = sentiment_classifier(text)[0]
        label = result['label']
        mapped_sentiment = SENTIMENT_MAPPING.get(label, "neutral")
        if mapped_sentiment == "neutral":
            logger.warning(f"Unknown sentiment label: {label}. Defaulting to 'neutral'.")
        return mapped_sentiment, result['score']
    except Exception as e:
        logger.error(f"Sentiment detection failed: {e}")
        raise MessageProcessingError(f"Sentiment detection failed: {str(e)}")
    