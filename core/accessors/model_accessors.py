# emotion_detector.py
from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="model/full_emotion_model",
)

stress_classifier = pipeline(
    "text-classification",
    model="model/full_stress_analysis_model",
)

sentiment_classifier = pipeline(
    "sentiment-analysis",
    model="model/full_sentiment_model",
)
