"""
Chatbot models for emotional support and conversation management.
Based on the reference implementation with adaptations for emotional wellbeing support.
"""
from django.db import models
from django.conf import settings
from core.models.base_model import AbstractBaseModel
import secrets
import json


def generate_secure_random_id():
    """Generate a secure random ID for conversations."""
    min_value = 10 ** 10  # Minimum value of the range (inclusive)
    max_value = 10 ** 11 - 1  # Maximum value of the range (exclusive)
    return secrets.randbelow(max_value - min_value) + min_value


class ConversationMemory(AbstractBaseModel):
    """
    Model to store conversation-level memory and context for emotional support.
    """
    MEMORY_TYPE_CHOICES = [
        ('short_term', 'Short Term'),
        ('long_term', 'Long Term'),
        ('episodic', 'Episodic'),
        ('semantic', 'Semantic'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memories')
    memory_type = models.CharField(max_length=20, choices=MEMORY_TYPE_CHOICES)
    title = models.CharField(max_length=255, help_text="Title or key for the memory")
    content = models.TextField(help_text="Memory content")
    context = models.JSONField(default=dict, help_text="Additional context data")
    importance_score = models.FloatField(default=0.0, help_text="Memory importance score (0-1)")
    access_count = models.IntegerField(default=0, help_text="How many times this memory was accessed")
    last_accessed = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this memory expires")
    
    class Meta:
        ordering = ['-importance_score', '-last_accessed']
        indexes = [
            models.Index(fields=['user', 'memory_type']),
            models.Index(fields=['importance_score']),
            models.Index(fields=['last_accessed']),
        ]
    
    def __str__(self):
        return f"{self.memory_type} memory: {self.title}"
    
    def increment_access(self):
        """Increment access count and update last accessed time"""
        self.access_count += 1
        self.save(update_fields=['access_count', 'last_accessed'])


class UserPersonality(AbstractBaseModel):
    """
    Model to store user personality traits and preferences for emotional support.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personality')
    communication_style = models.CharField(
        max_length=50, 
        default='empathetic', 
        help_text="empathetic, supportive, professional, casual"
    )
    emotional_state = models.CharField(
        max_length=50,
        default='neutral',
        help_text="Current emotional state detected from interactions"
    )
    stress_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('moderate', 'Moderate'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='low'
    )
    interests = models.JSONField(default=list, help_text="List of user interests")
    preferences = models.JSONField(default=dict, help_text="User preferences and settings")
    conversation_patterns = models.JSONField(default=dict, help_text="Learned conversation patterns")
    support_preferences = models.JSONField(
        default=dict, 
        help_text="Preferred types of emotional support (listening, advice, resources, etc.)"
    )
    
    def __str__(self):
        return f"Personality profile for {self.user.username}"


class Conversation(AbstractBaseModel):
    """
    Conversation model representing a chat conversation with emotional support context.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('ended', 'Ended'),
        ('requires_attention', 'Requires Attention'),  # For high stress situations
    ]

    id = models.BigIntegerField(primary_key=True, default=generate_secure_random_id, editable=False)
    title = models.CharField(max_length=255, default="Emotional Support Chat")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    favourite = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Emotional support specific fields
    conversation_summary = models.TextField(blank=True, help_text="AI-generated summary of the conversation")
    key_topics = models.JSONField(default=list, help_text="Important topics discussed")
    emotional_analysis = models.JSONField(default=dict, help_text="Overall emotional analysis of conversation")
    context_window = models.JSONField(default=list, help_text="Recent context for memory")
    memory_anchors = models.JSONField(default=list, help_text="Important message IDs for memory retrieval")
    
    # Support tracking
    support_type_used = models.JSONField(
        default=list, 
        help_text="Types of support provided (listening, advice, resources, etc.)"
    )
    crisis_flags = models.JSONField(
        default=list, 
        help_text="Crisis or high-stress indicators detected"
    )
    follow_up_needed = models.BooleanField(default=False, help_text="Whether follow-up is needed")

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'follow_up_needed']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return f"Conversation {self.title} - {self.user.username}"
    
    def get_recent_context(self, limit=10):
        """Get recent messages for context"""
        return self.messages.order_by('-created_at')[:limit]


class Message(AbstractBaseModel):
    """
    Message model representing a message within a conversation with emotional analysis.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_from_user = models.BooleanField(default=True)
    in_reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    
    # Emotional analysis and context enhancement fields
    embedding_vector = models.JSONField(null=True, blank=True, help_text="Message embedding for similarity search")
    importance_score = models.FloatField(default=0.0, help_text="Message importance for memory retention")
    emotions = models.JSONField(default=dict, help_text="Detected emotions in the message")
    entities = models.JSONField(default=list, help_text="Named entities extracted from message")
    intent = models.CharField(max_length=100, blank=True, help_text="Detected user intent")
    
    # Support specific fields
    stress_indicators = models.JSONField(default=list, help_text="Stress indicators detected in message")
    support_request = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Type of support being requested (advice, listening, resources, etc.)"
    )
    crisis_level = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('low', 'Low'),
            ('moderate', 'Moderate'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='none'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
            models.Index(fields=['importance_score']),
            models.Index(fields=['crisis_level']),
            models.Index(fields=['is_from_user', 'created_at']),
        ]

    def __str__(self):
        return f"Message in {self.conversation.title}"


class ConversationContext(AbstractBaseModel):
    """
    Model to store dynamic conversation context for emotional support.
    """
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='context')
    current_topic = models.CharField(max_length=255, blank=True)
    user_mood = models.CharField(max_length=50, blank=True)
    emotional_state = models.CharField(max_length=50, blank=True)
    conversation_flow = models.JSONField(default=list, help_text="Flow of conversation topics")
    active_memories = models.JSONField(default=list, help_text="Currently active memory IDs")
    context_variables = models.JSONField(default=dict, help_text="Dynamic context variables")
    
    # Support context
    current_support_type = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Current type of support being provided"
    )
    escalation_needed = models.BooleanField(default=False)
    last_crisis_check = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Context for {self.conversation.title}"


class EmotionalSupportLog(AbstractBaseModel):
    """
    Log of emotional support actions taken during conversations.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='support_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_type = models.CharField(
        max_length=50,
        choices=[
            ('listening', 'Active Listening'),
            ('advice', 'Advice Given'),
            ('resources', 'Resources Provided'),
            ('validation', 'Emotional Validation'),
            ('crisis_response', 'Crisis Response'),
            ('follow_up', 'Follow-up Scheduled'),
        ]
    )
    action_description = models.TextField()
    effectiveness_score = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Effectiveness score based on user response"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', 'action_type']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action_type} for {self.user.username}"