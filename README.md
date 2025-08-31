# MindPulse - Employee Wellbeing Analytics Platform

A comprehensive Django-based platform for monitoring and supporting employee mental health and wellbeing through intelligent message analysis and AI-powered emotional support.

## 🚀 Features

### 📊 **Wellbeing Analytics**
- **Real-time Message Analysis**: Automatically analyzes messages from various communication channels (Discord, Slack, Teams, etc.)
- **ML-Powered Insights**: Uses custom-trained models for sentiment, emotion, and stress detection
- **Team Dashboard**: Comprehensive analytics dashboard for managers to monitor team wellbeing
- **Individual Tracking**: Personal wellbeing metrics and trends for employees
- **Multi-Channel Support**: Aggregates data across different communication platforms

### 🤖 **AI Emotional Support Chatbot**
- **OpenAI Integration**: Natural conversations powered by GPT models
- **Context-Aware**: Maintains conversation history and context for meaningful interactions
- **Crisis Detection**: Automatically identifies high-stress situations and provides appropriate support
- **Anonymous Access**: Works without authentication for privacy-conscious users
- **Emotional Analysis**: Real-time emotion and stress detection during conversations

### 📈 **Advanced Analytics**
- **Wellbeing Aggregation**: Automated daily aggregation of team and individual metrics
- **Trend Analysis**: Historical tracking of sentiment, stress, and emotional patterns
- **Alert System**: Proactive notifications for concerning wellbeing indicators
- **Channel Breakdown**: Analytics by communication channel (work vs personal communications)

### 🔧 **Technical Features**
- **Async Processing**: Celery-powered background task processing for ML analysis
- **RESTful APIs**: Comprehensive REST API for frontend integration
- **JWT Authentication**: Secure authentication with refresh tokens
- **Database Optimization**: Optimized models with proper indexing for analytics queries
- **Management Commands**: Django management commands for data sync and maintenance

## 🏗️ Architecture

### **Core Components**
```
mindpulse/
├── core/                    # Main application logic
│   ├── models/             # Data models (User, Message, Channel, etc.)
│   ├── services/           # Business logic and ML services
│   ├── views/              # API endpoints
│   ├── tasks/              # Celery background tasks
│   └── management/         # Django management commands
├── chatbot/                # AI chatbot functionality
│   ├── models/             # Conversation and memory models
│   ├── services/           # Chatbot logic and OpenAI integration
│   └── views/              # Chat API endpoints
└── model/                  # Trained ML models
    ├── full_sentiment_model/
    ├── full_emotion_model/
    └── full_stress_analysis_model/
```

### **ML Models**
- **Sentiment Analysis**: Classifies messages as positive/negative with confidence scores
- **Emotion Detection**: Identifies 6 emotions (joy, sadness, anger, fear, love, surprise)
- **Stress Detection**: Detects stress indicators in communications

### **Background Processing**
- **Message Analysis**: Async processing of incoming messages
- **Wellbeing Aggregation**: Periodic aggregation of analytics data
- **Data Cleanup**: Automated cleanup of old data and optimization

## 📡 API Endpoints

### **Message Ingestion**
```http
POST /api/messages/
Content-Type: application/json

{
  "channel_id": "uuid",
  "username": "employee_username", 
  "message": "message content",
  "external_ref": "optional_reference"
}
```

### **Analytics Dashboard**
```http
GET /api/analytics/team/?start_date=2025-08-01T00:00:00Z&end_date=2025-08-31T23:59:59Z
Authorization: Bearer <jwt_token>
```

### **Chatbot APIs**
```http
# Send message to chatbot
POST /api/chatbot/chat/
{
  "message": "I need help with stress",
  "conversation_id": null  // null for new conversation
}

# Get conversation history
GET /api/chatbot/conversations/{conversation_id}/messages/

# List all conversations
GET /api/chatbot/conversations/
```

### **Channel Management**
```http
POST /api/channels/
{
  "name": "team-general",
  "type": "discord",
  "external_id": "channel_123"
}
```

## 🛠️ Setup & Installation

### **Prerequisites**
- Python 3.10+
- Redis (for Celery broker)
- SQLite (default) or PostgreSQL

### **Installation**
```bash
# Clone repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
# or env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
export OPENAI_API_KEY="your-openai-api-key"
export SECRET_KEY="your-django-secret-key"
export DEBUG="True"  # For development

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start services
python manage.py runserver          # Django server (Terminal 1)
celery -A mindpulse worker -l info  # Celery worker (Terminal 2)
celery -A mindpulse beat -l info    # Celery scheduler (Terminal 3)
redis-server                        # Redis (Terminal 4)
```

## 📊 ML Model Performance

### **Indicator Meanings**
- **Sentiment Score**: 0.0-1.0 confidence level
  - `positive` + high score = Very positive message
  - `negative` + high score = Very negative message
- **Stress Detection**: `true`/`false` with confidence
  - `true` + 0.99 = Very confident stress detected
- **Emotion Scores**: 0.0-1.0 confidence for detected emotion
- **Aggregated Metrics**: -1.0 to +1.0 weighted averages
  - Positive values = Good wellbeing
  - Negative values = Concerning trends

## 🔄 Background Tasks

### **Automatic Tasks**
- **Message Analysis**: Processes new messages with ML models
- **Wellbeing Aggregation**: Runs every 30 minutes to update analytics
- **Data Cleanup**: Daily cleanup of old data

### **Management Commands**
```bash
# Sync messages without analysis
python manage.py sync_message_analysis

# Options for sync command
python manage.py sync_message_analysis --dry-run     # Preview what will be processed
python manage.py sync_message_analysis --limit 100   # Process only 100 messages
python manage.py sync_message_analysis --batch-size 50  # Process in batches of 50
```

## 📱 Frontend Integration

### **Message Analysis Response**
```json
{
  "data": {
    "processed_messages": [{
      "message_id": "uuid",
      "status": "queued_for_analysis"
    }]
  }
}
```

### **Analytics Dashboard Response**
```json
{
  "data": {
    "team_overview": {
      "sentiment_weighted_avg": 0.45,    // Positive team sentiment
      "stress_weighted_avg": -0.2,       // Low team stress
      "emotions": {
        "joy": 0.6,
        "sadness": 0.1,
        "anger": 0.05
      },
      "wellbeing_score": 7.2,           // Overall score out of 10
      "alert_level": "normal"
    }
  }
}
```

### **Chatbot Response**
```json
{
  "data": {
    "conversation_id": 12345,
    "message": "I understand you're feeling stressed...",
    "support_type": "listening",
    "user_message_analysis": {
      "sentiment": "negative",
      "stress_detected": true,
      "crisis_level": "low"
    },
    "escalation_needed": false
  }
}
```

## 🔐 Security & Privacy

### **Authentication**
- JWT-based authentication for secure API access
- Role-based access control (employee/manager/admin)
- Session management with secure cookies

### **Privacy Features**
- Anonymous chatbot access for sensitive conversations
- User data hashing for privacy protection
- Configurable data retention policies

### **Security Headers**
- CORS configuration for frontend integration
- CSRF protection
- XSS filtering
- Secure session management

## 🚨 Monitoring & Alerts

### **Health Monitoring**
- System health checks every 5 minutes
- Database connectivity monitoring
- ML model availability checks
- Performance metrics tracking

### **Crisis Detection**
- Automatic detection of stress keywords
- Crisis level escalation (none/low/moderate/high/critical)
- Support action logging
- Follow-up scheduling for high-risk situations

## 📋 Data Models

### **Key Models**
- **User**: Employee profiles with role-based permissions
- **Channel**: Communication channels (Discord, Slack, etc.)
- **Message**: Individual messages with metadata
- **MessageAnalysis**: ML analysis results for each message
- **WellbeingAggregate**: Aggregated analytics data
- **Conversation**: Chatbot conversation threads
- **ConversationMemory**: Context and memory for AI interactions

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
SECRET_KEY=your-django-secret-key
DEBUG=True
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

### **Celery Configuration**
- Simple queue configuration for reliable task processing
- Automatic task discovery
- Periodic task scheduling
- Error handling and logging

## 📊 Analytics Features

### **Team Analytics**
- Sentiment trends over time
- Stress level monitoring
- Emotion distribution analysis
- Message volume tracking
- Channel-wise breakdowns

### **Individual Analytics**
- Personal wellbeing scores
- Communication pattern analysis
- Stress indicator tracking
- Emotional state monitoring

## 🤖 Chatbot Capabilities

### **Emotional Support**
- Empathetic conversation handling
- Crisis situation recognition
- Support type classification (listening, advice, resources)
- Memory management for context retention

### **Integration Features**
- Works with existing ML models
- Real-time emotion analysis during conversations
- Escalation protocols for high-risk situations
- Support action logging and tracking

## 🚀 Production Considerations

### **Scalability**
- Optimized database queries with proper indexing
- Async task processing for ML operations
- Configurable batch sizes for large datasets
- Database connection pooling

### **Performance**
- Redis caching for frequently accessed data
- Optimized aggregation queries
- Background processing for heavy ML operations
- Rate limiting for API endpoints

### **Monitoring**
- Comprehensive logging configuration
- Error tracking and reporting
- Performance metrics collection
- Health check endpoints

## 📞 Support & Documentation

- **API Documentation**: `api_docs.json` - Complete API reference
- **Chat API**: `chat_api.json` - Chatbot API documentation  
- **Indicators Guide**: `INDICATORS_GUIDE.md` - ML model interpretation guide
- **Database Optimization**: `DATABASE_OPTIMIZATION_GUIDE.md` - Performance tuning guide

## 🔄 Workflow

1. **Message Ingestion**: External services send messages via API
2. **ML Processing**: Background tasks analyze messages for sentiment/emotion/stress
3. **Data Aggregation**: Periodic aggregation creates analytics summaries
4. **Dashboard Access**: Managers view team analytics through web dashboard
5. **Support Intervention**: Chatbot provides immediate emotional support when needed

## 🎯 Use Cases

- **HR Teams**: Monitor employee wellbeing trends and identify at-risk individuals
- **Managers**: Get insights into team morale and stress levels
- **Employees**: Access confidential emotional support through AI chatbot
- **Organizations**: Data-driven approach to workplace mental health initiatives
- **Crisis Response**: Early intervention for employees showing stress indicators

---

**MindPulse** - Empowering organizations to build healthier, more supportive work environments through intelligent wellbeing analytics and AI-powered emotional support.