from django.contrib import admin
from chatbot.models import ConversationMemory, Conversation, UserPersonality, Message, ConversationContext, EmotionalSupportLog
# Register your models here.
admin.site.register([ConversationMemory, Conversation, UserPersonality, Message, ConversationContext, EmotionalSupportLog])