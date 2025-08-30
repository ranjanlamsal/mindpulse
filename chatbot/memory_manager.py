"""
Memory management utilities for the emotional support chatbot.
Handles short-term and long-term memory operations with emotional context.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.db.models import Q, F
from django.conf import settings
from .models import ConversationMemory, UserPersonality, Conversation, Message, ConversationContext

logger = logging.getLogger(__name__)


class EmotionalMemoryManager:
    """
    Manages short-term and long-term memory for the emotional support chatbot.
    """
    
    def __init__(self, user):
        self.user = user
        self.short_term_limit = getattr(settings, 'CHATBOT_SHORT_TERM_MEMORY_LIMIT', 20)
        self.long_term_importance_threshold = getattr(settings, 'CHATBOT_LONG_TERM_IMPORTANCE_THRESHOLD', 0.7)
    
    def get_short_term_memory(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve short-term memory items with emotional context.
        """
        if limit is None:
            limit = self.short_term_limit
        
        memories = ConversationMemory.objects.filter(
            user=self.user,
            memory_type='short_term'
        ).order_by('-last_accessed')[:limit]
        
        return [self._memory_to_dict(memory) for memory in memories]
    
    def get_long_term_memory(self, query: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve long-term memory items, optionally filtered by query.
        """
        queryset = ConversationMemory.objects.filter(
            user=self.user,
            memory_type='long_term'
        )
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query)
            )
        
        memories = queryset.order_by('-importance_score', '-last_accessed')[:limit]
        
        # Increment access count for retrieved memories
        for memory in memories:
            memory.increment_access()
        
        return [self._memory_to_dict(memory) for memory in memories]
    
    def get_emotional_context_memory(self, emotion: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories related to specific emotional context.
        """
        memories = ConversationMemory.objects.filter(
            user=self.user,
            context__emotional_state=emotion
        ).order_by('-importance_score', '-last_accessed')[:limit]
        
        for memory in memories:
            memory.increment_access()
        
        return [self._memory_to_dict(memory) for memory in memories]
    
    def store_short_term_memory(self, title: str, content: str, context: Dict = None, importance: float = 0.5):
        """
        Store a short-term memory item with emotional context.
        """
        # Set expiration for short-term memory (24 hours)
        expires_at = timezone.now() + timedelta(hours=24)
        
        # Enhance context with emotional information
        enhanced_context = context or {}
        if hasattr(self.user, 'personality'):
            enhanced_context['emotional_state'] = self.user.personality.emotional_state
            enhanced_context['stress_level'] = self.user.personality.stress_level
        
        memory = ConversationMemory.objects.create(
            user=self.user,
            memory_type='short_term',
            title=title,
            content=content,
            context=enhanced_context,
            importance_score=importance,
            expires_at=expires_at
        )
        
        # Clean up old short-term memories
        self._cleanup_short_term_memory()
        
        return memory
    
    def store_long_term_memory(self, title: str, content: str, context: Dict = None, importance: float = 0.8):
        """
        Store a long-term memory item with emotional significance.
        """
        enhanced_context = context or {}
        if hasattr(self.user, 'personality'):
            enhanced_context['emotional_state'] = self.user.personality.emotional_state
            enhanced_context['stress_level'] = self.user.personality.stress_level
        
        memory = ConversationMemory.objects.create(
            user=self.user,
            memory_type='long_term',
            title=title,
            content=content,
            context=enhanced_context,
            importance_score=importance
        )
        
        return memory
    
    def store_crisis_memory(self, title: str, content: str, context: Dict = None):
        """
        Store a crisis-related memory with high importance.
        """
        crisis_context = context or {}
        crisis_context.update({
            'memory_type': 'crisis',
            'requires_attention': True,
            'timestamp': timezone.now().isoformat()
        })
        
        return self.store_long_term_memory(
            title=f"CRISIS: {title}",
            content=content,
            context=crisis_context,
            importance=1.0
        )
    
    def get_conversation_context(self, conversation_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent conversation context for memory-aware responses.
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=self.user)
            recent_messages = conversation.get_recent_context(limit)
            
            # Get conversation context if exists
            context_data = {}
            if hasattr(conversation, 'context'):
                context_obj = conversation.context
                context_data = {
                    'current_topic': context_obj.current_topic,
                    'user_mood': context_obj.user_mood,
                    'emotional_state': context_obj.emotional_state,
                    'conversation_flow': context_obj.conversation_flow,
                    'active_memories': context_obj.active_memories,
                    'current_support_type': context_obj.current_support_type,
                    'escalation_needed': context_obj.escalation_needed
                }
            
            return {
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'status': conversation.status,
                    'summary': conversation.conversation_summary,
                    'key_topics': conversation.key_topics,
                    'crisis_flags': conversation.crisis_flags,
                    'follow_up_needed': conversation.follow_up_needed
                },
                'recent_messages': [
                    {
                        'id': msg.id,
                        'content': msg.content,
                        'is_from_user': msg.is_from_user,
                        'emotions': msg.emotions,
                        'crisis_level': msg.crisis_level,
                        'support_request': msg.support_request,
                        'created_at': msg.created_at.isoformat()
                    } for msg in recent_messages
                ],
                'context': context_data,
                'user_personality': self._get_user_personality()
            }
        except Conversation.DoesNotExist:
            return {}
    
    def update_conversation_context(self, conversation_id: str, **updates):
        """
        Update conversation context with new information.
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=self.user)
            context, created = ConversationContext.objects.get_or_create(
                conversation=conversation,
                defaults=updates
            )
            
            if not created:
                for key, value in updates.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
                context.save()
            
            return context
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {conversation_id} not found for user {self.user.id}")
            return None
    
    def promote_to_long_term(self, short_term_memory_id: int):
        """
        Promote a short-term memory to long-term based on importance.
        """
        try:
            memory = ConversationMemory.objects.get(
                id=short_term_memory_id,
                user=self.user,
                memory_type='short_term'
            )
            
            if memory.importance_score >= self.long_term_importance_threshold:
                memory.memory_type = 'long_term'
                memory.expires_at = None  # Long-term memories don't expire
                memory.save()
                
                logger.info(f"Promoted memory {memory.id} to long-term for user {self.user.id}")
                return True
            
            return False
        except ConversationMemory.DoesNotExist:
            return False
    
    def _cleanup_short_term_memory(self):
        """
        Clean up expired and excess short-term memories.
        """
        # Remove expired memories
        ConversationMemory.objects.filter(
            user=self.user,
            memory_type='short_term',
            expires_at__lte=timezone.now()
        ).delete()
        
        # Keep only the most recent memories if over limit
        excess_memories = ConversationMemory.objects.filter(
            user=self.user,
            memory_type='short_term'
        ).order_by('-last_accessed')[self.short_term_limit:]
        
        if excess_memories:
            # Try to promote important memories before deletion
            for memory in excess_memories:
                if not self.promote_to_long_term(memory.id):
                    memory.delete()
    
    def _memory_to_dict(self, memory) -> Dict[str, Any]:
        """
        Convert memory object to dictionary for API responses.
        """
        return {
            'id': memory.id,
            'type': memory.memory_type,
            'title': memory.title,
            'content': memory.content,
            'context': memory.context,
            'importance_score': memory.importance_score,
            'access_count': memory.access_count,
            'created_at': memory.created_at.isoformat(),
            'last_accessed': memory.last_accessed.isoformat()
        }
    
    def _get_user_personality(self) -> Dict[str, Any]:
        """
        Get user personality information for context.
        """
        try:
            personality = self.user.personality
            return {
                'communication_style': personality.communication_style,
                'emotional_state': personality.emotional_state,
                'stress_level': personality.stress_level,
                'interests': personality.interests,
                'preferences': personality.preferences,
                'support_preferences': personality.support_preferences
            }
        except:
            # Create default personality if doesn't exist
            personality = UserPersonality.objects.create(user=self.user)
            return {
                'communication_style': personality.communication_style,
                'emotional_state': personality.emotional_state,
                'stress_level': personality.stress_level,
                'interests': personality.interests,
                'preferences': personality.preferences,
                'support_preferences': personality.support_preferences
            }
    
    def analyze_conversation_patterns(self) -> Dict[str, Any]:
        """
        Analyze user's conversation patterns for better emotional support.
        """
        recent_conversations = Conversation.objects.filter(
            user=self.user
        ).order_by('-updated_at')[:10]
        
        patterns = {
            'frequent_topics': [],
            'emotional_trends': [],
            'crisis_patterns': [],
            'support_effectiveness': {}
        }
        
        for conv in recent_conversations:
            # Analyze key topics
            patterns['frequent_topics'].extend(conv.key_topics)
            
            # Analyze emotional trends
            if conv.emotional_analysis:
                patterns['emotional_trends'].append(conv.emotional_analysis)
            
            # Check for crisis patterns
            if conv.crisis_flags:
                patterns['crisis_patterns'].extend(conv.crisis_flags)
        
        return patterns