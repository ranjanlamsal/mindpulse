"""
Emotional support chatbot services with OpenAI integration.
Provides empathetic responses and crisis detection.
"""
import openai
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from chatbot.models import Conversation, Message, ConversationContext, EmotionalSupportLog, UserPersonality
from chatbot.memory_manager import EmotionalMemoryManager
from core.services.model_services import detect_sentiment, detect_emotion, detect_stress

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = settings.OPENAI_API_KEY


class EmotionalSupportChatbotService:
    """
    Main service for emotional support chatbot functionality.
    """
    
    def __init__(self, user):
        self.user = user
        self.memory_manager = EmotionalMemoryManager(user) if user else None
        self.model = settings.OPENAI_MODEL
        
    def process_user_message(self, conversation_id: int, message_content: str) -> Dict[str, Any]:
        """
        Process user message and generate empathetic response.
        """
        try:
            # Get or create conversation
            conversation = self._get_or_create_conversation(conversation_id)
            
            # Store user message
            user_message = self._store_message(conversation, message_content, is_from_user=True)
            
            # Analyze user message for emotional content and crisis indicators
            analysis = self._analyze_message(user_message)
            
            # Update conversation context
            self._update_conversation_context(conversation, analysis)
            
            # Generate empathetic response
            bot_response = self._generate_response(conversation, user_message, analysis)
            
            # Store bot response
            bot_message = self._store_message(conversation, bot_response['content'], is_from_user=False)
            
            # Log support action
            self._log_support_action(conversation, analysis, bot_response['support_type'])
            
            # Check if escalation is needed
            escalation_needed = self._check_escalation_needed(analysis, conversation)
            
            return {
                'conversation_id': conversation.id,
                'message': bot_response['content'],
                'support_type': bot_response['support_type'],
                'user_message_analysis': analysis,
                'escalation_needed': escalation_needed,
                'conversation_status': conversation.status,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            user_id = self.user.id if self.user else 'anonymous'
            logger.error(f"Error processing message for user {user_id}: {str(e)}")
            return {
                'error': 'Unable to process message at this time.',
                'support_message': "I'm here to listen. Please feel free to share what's on your mind when you're ready."
            }
    
    def get_conversation_history(self, conversation_id: int, limit: int = 50) -> List[Dict]:
        """
        Get conversation history for a specific conversation.
        """
        try:
            # For POC, allow access to any conversation by ID
            conversation = Conversation.objects.get(id=conversation_id)
            messages = conversation.messages.order_by('created_at')[:limit]
            
            return [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'is_from_user': msg.is_from_user,
                    'emotions': msg.emotions,
                    'crisis_level': msg.crisis_level,
                    'support_request': msg.support_request,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in messages
            ]
        except Conversation.DoesNotExist:
            return []
    
    def list_conversations(self) -> List[Dict]:
        """
        List all conversations for the user.
        """
        # For POC, show all recent conversations regardless of user
        conversations = Conversation.objects.all().order_by('-updated_at')[:20]
        
        return [
            {
                'id': conv.id,
                'title': conv.title,
                'status': conv.status,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'favourite': conv.favourite,
                'archive': conv.archive,
                'follow_up_needed': conv.follow_up_needed,
                'crisis_flags': conv.crisis_flags,
                'last_message_preview': self._get_last_message_preview(conv)
            }
            for conv in conversations
        ]
    
    def _get_or_create_conversation(self, conversation_id: Optional[int] = None) -> Conversation:
        """
        Get existing conversation or create a new one.
        """
        if conversation_id:
            try:
                if self.user:
                    return Conversation.objects.get(id=conversation_id, user=self.user)
                else:
                    # For anonymous users, try to get conversation without user constraint
                    return Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                pass
        
        # Create new conversation
        conversation = Conversation.objects.create(
            user=self.user,  # Can be None for anonymous users
            title=f"Emotional Support Chat - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Create initial context
        ConversationContext.objects.create(conversation=conversation)
        
        return conversation
    
    def _store_message(self, conversation: Conversation, content: str, is_from_user: bool) -> Message:
        """
        Store a message in the conversation.
        """
        message = Message.objects.create(
            conversation=conversation,
            content=content,
            is_from_user=is_from_user
        )
        
        # Update conversation timestamp
        conversation.save(update_fields=['updated_at'])
        
        return message
    
    def _analyze_message(self, message: Message) -> Dict[str, Any]:
        """
        Analyze message for emotional content and crisis indicators.
        """
        try:
            # Use existing ML models for analysis
            sentiment, sentiment_score = detect_sentiment(message.content)
            emotion, emotion_score = detect_emotion(message.content)
            stress_detected, stress_score = detect_stress(message.content)
            
            # Detect crisis indicators
            crisis_level, crisis_indicators = self._detect_crisis_indicators(message.content)
            
            # Detect support request type
            support_request = self._detect_support_request(message.content)
            
            # Extract entities and intent
            entities = self._extract_entities(message.content)
            intent = self._detect_intent(message.content)
            
            # Calculate importance score
            importance_score = self._calculate_importance_score(
                sentiment_score, emotion_score, stress_score, crisis_level
            )
            
            # Update message with analysis
            message.emotions = {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'emotion': emotion,
                'emotion_score': emotion_score
            }
            message.stress_indicators = ['stress'] if stress_detected else []
            message.crisis_level = crisis_level
            message.support_request = support_request
            message.entities = entities
            message.intent = intent
            message.importance_score = importance_score
            message.save()
            
            return {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'emotion': emotion,
                'emotion_score': emotion_score,
                'stress_detected': stress_detected,
                'stress_score': stress_score,
                'crisis_level': crisis_level,
                'crisis_indicators': crisis_indicators,
                'support_request': support_request,
                'entities': entities,
                'intent': intent,
                'importance_score': importance_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0.5,
                'emotion': 'neutral',
                'emotion_score': 0.5,
                'stress_detected': False,
                'stress_score': 0.0,
                'crisis_level': 'none',
                'crisis_indicators': [],
                'support_request': 'listening',
                'entities': [],
                'intent': 'general_support',
                'importance_score': 0.3
            }
    
    def _generate_response(self, conversation: Conversation, user_message: Message, analysis: Dict) -> Dict[str, Any]:
        """
        Generate empathetic response using OpenAI.
        """
        try:
            # Get conversation context
            context = self.memory_manager.get_conversation_context(conversation.id) if self.memory_manager else {}
            
            # Build system prompt for emotional support
            system_prompt = self._build_system_prompt(analysis, context)
            
            # Build conversation history for context
            conversation_history = self._build_conversation_history(conversation)
            
            # Generate response
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *conversation_history,
                    {"role": "user", "content": user_message.content}
                ],
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            bot_response = response.choices[0].message.content
            support_type = self._determine_support_type(analysis, bot_response)
            
            return {
                'content': bot_response,
                'support_type': support_type
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(analysis)
    
    def _build_system_prompt(self, analysis: Dict, context: Dict) -> str:
        """
        Build system prompt for emotional support chatbot.
        """
        user_personality = context.get('user_personality', {})
        communication_style = user_personality.get('communication_style', 'empathetic')
        stress_level = user_personality.get('stress_level', 'low')
        crisis_level = analysis.get('crisis_level', 'none')
        
        base_prompt = f"""You are an empathetic emotional support chatbot designed to help employees with their mental wellbeing. Your communication style should be {communication_style}.

Current user context:
- Emotional state: {user_personality.get('emotional_state', 'neutral')}
- Stress level: {stress_level}
- Crisis level detected: {crisis_level}
- Support preferences: {user_personality.get('support_preferences', {})}

Guidelines:
1. Always be empathetic, understanding, and non-judgmental
2. Validate the user's feelings and experiences
3. Provide emotional support through active listening
4. Offer practical coping strategies when appropriate
5. If crisis indicators are detected, provide immediate support resources
6. Encourage professional help for serious concerns
7. Keep responses conversational and supportive
8. Ask follow-up questions to show engagement
9. Remember context from the conversation

"""
        
        if crisis_level in ['high', 'critical']:
            base_prompt += """
CRISIS ALERT: The user is showing signs of high distress. Prioritize:
- Immediate emotional validation
- Crisis support resources
- Encourage professional help
- Provide crisis hotline information if needed
- Stay with them and show you care
"""
        
        return base_prompt
    
    def _build_conversation_history(self, conversation: Conversation, limit: int = 10) -> List[Dict]:
        """
        Build conversation history for OpenAI context.
        """
        recent_messages = conversation.messages.order_by('-created_at')[:limit]
        history = []
        
        for msg in reversed(recent_messages):
            role = "user" if msg.is_from_user else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })
        
        return history[-limit:]  # Keep only recent messages
    
    def _detect_crisis_indicators(self, content: str) -> Tuple[str, List[str]]:
        """
        Detect crisis indicators in user message.
        """
        crisis_keywords = {
            'critical': ['suicide', 'kill myself', 'end it all', 'not worth living', 'want to die'],
            'high': ['can\'t go on', 'overwhelming', 'breaking point', 'can\'t handle', 'give up'],
            'moderate': ['very stressed', 'anxious', 'depressed', 'struggling', 'difficult time'],
            'low': ['worried', 'concerned', 'stressed', 'tired', 'overwhelmed']
        }
        
        content_lower = content.lower()
        detected_indicators = []
        crisis_level = 'none'
        
        for level, keywords in crisis_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    detected_indicators.append(keyword)
                    if level == 'critical':
                        crisis_level = 'critical'
                    elif level == 'high' and crisis_level != 'critical':
                        crisis_level = 'high'
                    elif level == 'moderate' and crisis_level not in ['critical', 'high']:
                        crisis_level = 'moderate'
                    elif level == 'low' and crisis_level == 'none':
                        crisis_level = 'low'
        
        return crisis_level, detected_indicators
    
    def _detect_support_request(self, content: str) -> str:
        """
        Detect what type of support the user is requesting.
        """
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['advice', 'what should i', 'help me', 'suggest']):
            return 'advice'
        elif any(word in content_lower for word in ['listen', 'hear me', 'understand', 'feel']):
            return 'listening'
        elif any(word in content_lower for word in ['resource', 'help', 'support', 'information']):
            return 'resources'
        else:
            return 'listening'  # Default to listening
    
    def _extract_entities(self, content: str) -> List[str]:
        """
        Extract named entities from the message (simplified).
        """
        # This is a simplified implementation
        # In production, you might use spaCy or similar NLP library
        entities = []
        
        # Common workplace entities
        workplace_terms = ['work', 'boss', 'colleague', 'team', 'project', 'deadline', 'meeting']
        personal_terms = ['family', 'friend', 'relationship', 'health', 'money', 'home']
        
        content_lower = content.lower()
        for term in workplace_terms + personal_terms:
            if term in content_lower:
                entities.append(term)
        
        return list(set(entities))  # Remove duplicates
    
    def _detect_intent(self, content: str) -> str:
        """
        Detect user intent from message.
        """
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['hello', 'hi', 'hey', 'good morning']):
            return 'greeting'
        elif any(word in content_lower for word in ['bye', 'goodbye', 'talk later', 'thanks']):
            return 'closing'
        elif any(word in content_lower for word in ['help', 'support', 'advice']):
            return 'seeking_help'
        elif any(word in content_lower for word in ['feeling', 'feel', 'emotion', 'mood']):
            return 'emotional_expression'
        else:
            return 'general_support'
    
    def _calculate_importance_score(self, sentiment_score: float, emotion_score: float, 
                                  stress_score: float, crisis_level: str) -> float:
        """
        Calculate importance score for memory storage.
        """
        base_score = (abs(sentiment_score - 0.5) * 2 + emotion_score + stress_score) / 3
        
        crisis_multiplier = {
            'none': 1.0,
            'low': 1.2,
            'moderate': 1.5,
            'high': 1.8,
            'critical': 2.0
        }
        
        return min(1.0, base_score * crisis_multiplier.get(crisis_level, 1.0))
    
    def _update_conversation_context(self, conversation: Conversation, analysis: Dict):
        """
        Update conversation context with new analysis.
        """
        context_updates = {
            'user_mood': analysis['emotion'],
            'emotional_state': analysis['sentiment'],
            'current_support_type': analysis['support_request'],
            'escalation_needed': analysis['crisis_level'] in ['high', 'critical'],
            'last_crisis_check': timezone.now() if analysis['crisis_level'] != 'none' else None
        }
        
        if self.memory_manager:
            self.memory_manager.update_conversation_context(conversation.id, **context_updates)
        
        # Update conversation flags
        if analysis['crisis_level'] in ['high', 'critical']:
            conversation.crisis_flags = list(set(conversation.crisis_flags + analysis['crisis_indicators']))
            conversation.status = 'requires_attention'
            conversation.follow_up_needed = True
            conversation.save()
    
    def _determine_support_type(self, analysis: Dict, response: str) -> str:
        """
        Determine what type of support was provided in the response.
        """
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['suggest', 'try', 'might help', 'consider']):
            return 'advice'
        elif any(word in response_lower for word in ['understand', 'hear you', 'valid', 'normal']):
            return 'validation'
        elif any(word in response_lower for word in ['resource', 'help', 'support', 'contact']):
            return 'resources'
        elif any(word in response_lower for word in ['crisis', 'urgent', 'immediate', 'emergency']):
            return 'crisis_response'
        else:
            return 'listening'
    
    def _log_support_action(self, conversation: Conversation, analysis: Dict, support_type: str):
        """
        Log the support action taken.
        """
        EmotionalSupportLog.objects.create(
            conversation=conversation,
            user=self.user,  # Can be None for anonymous users
            action_type=support_type,
            action_description=f"Provided {support_type} support for {analysis['emotion']} emotion with {analysis['crisis_level']} crisis level"
        )
    
    def _check_escalation_needed(self, analysis: Dict, conversation: Conversation) -> bool:
        """
        Check if human escalation is needed.
        """
        # Escalate if critical crisis level
        if analysis['crisis_level'] == 'critical':
            return True
        
        # Escalate if high stress persists
        if analysis['crisis_level'] == 'high' and len(conversation.crisis_flags) > 3:
            return True
        
        return False
    
    def _get_fallback_response(self, analysis: Dict) -> Dict[str, Any]:
        """
        Get fallback response when OpenAI fails.
        """
        crisis_level = analysis.get('crisis_level', 'none')
        
        if crisis_level in ['high', 'critical']:
            return {
                'content': "I can sense you're going through a really difficult time right now. Your feelings are valid, and you don't have to face this alone. Please consider reaching out to a mental health professional or a crisis support line. I'm here to listen if you'd like to share more about what you're experiencing.",
                'support_type': 'crisis_response'
            }
        else:
            return {
                'content': "I hear you, and I want you to know that your feelings are valid. Sometimes it helps just to have someone listen. Would you like to tell me more about what's on your mind?",
                'support_type': 'listening'
            }
    
    def _get_last_message_preview(self, conversation: Conversation) -> str:
        """
        Get preview of the last message in conversation.
        """
        last_message = conversation.messages.order_by('-created_at').first()
        if last_message:
            preview = last_message.content[:100]
            return preview + "..." if len(last_message.content) > 100 else preview
        return "No messages yet"
    