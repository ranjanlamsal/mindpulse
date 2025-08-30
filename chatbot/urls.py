from django.urls import path
from .views import ChatbotSessionView, ChatbotMessageView

urlpatterns = [
    path("session/", ChatbotSessionView.as_view(), name="chatbot-session"),
    path("message/", ChatbotMessageView.as_view(), name="chatbot-message"),
]
