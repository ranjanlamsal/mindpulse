# MindPulse API Documentation

## Overview
MindPulse is a comprehensive wellbeing analytics platform that processes messages from various communication channels (Discord, Teams, Jira, etc.) and provides AI-powered sentiment analysis, emotional state detection, and team wellbeing insights.

**Base URL:** `http://your-domain.com/api/`

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Response Format
All API responses follow a consistent format:

### Success Response
```json
{
  "data": {},
  "message": "Success message",
  "timestamp": "2025-08-30T19:00:00Z",
  "success": true
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "error_code": "ERROR_CODE",
  "errors": {},
  "timestamp": "2025-08-30T19:00:00Z"
}
```

---

## 🔐 Authentication Endpoints

### 1. User Registration
**POST** `/auth/register/`

Register a new user (employees only).

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@company.com",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "role": "employee"
}
```

**Response (201 Created):**
```json
{
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@company.com",
      "role": "employee",
      "hashed_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-08-30T10:00:00Z",
      "is_active": true,
      "last_login_at": null,
      "message_count": 0,
      "last_activity": null
    }
  },
  "message": "Registration successful",
  "success": true,
  "timestamp": "2025-08-30T10:00:00Z"
}
```

### 2. User Login
**POST** `/auth/login/`

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@company.com",
      "role": "employee",
      "hashed_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-08-30T10:00:00Z",
      "is_active": true,
      "last_login_at": "2025-08-30T15:30:00Z",
      "message_count": 42,
      "last_activity": "2025-08-30T14:45:00Z"
    }
  },
  "message": "Login successful",
  "success": true,
  "timestamp": "2025-08-30T15:30:00Z"
}
```

### 3. Token Refresh
**POST** `/auth/token/refresh/`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Role-based Dashboards
**GET** `/auth/dashboard/employee/` (🔒 Employee+)
**GET** `/auth/dashboard/manager/` (🔒 Manager+)  
**GET** `/auth/dashboard/admin/` (🔒 Admin only)

Get role-specific dashboard data.

---

## 📊 Data Ingestion Endpoints

### 1. Create/Get Channel
**POST** `/channels/`

Create or retrieve a communication channel.

**Request Body:**
```json
{
  "name": "General Discussion",
  "type": "discord",
  "external_id": "discord_123456789"
}
```

**Response (201 Created / 200 OK):**
```json
{
  "message": "Channel Created Successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "General Discussion",
    "external_id": "discord_123456789",
    "type": "discord"
  }
}
```

**Channel Types:**
- `discord` - Discord channels
- `meeting` - Meeting transcripts
- `jira` - Jira comments
- `chat` - General chat applications

### 2. Message Ingestion
**POST** `/messages/`

Ingest messages for analysis. Accepts single message or array of messages.

**Request Body (Single Message):**
```json
{
  "channel_id": "550e8400-e29b-41d4-a716-446655440000",
  "external_ref": "msg-123456",
  "username": "john_doe",
  "message": "I'm feeling overwhelmed with the current project deadline."
}
```

**Request Body (Multiple Messages):**
```json
[
  {
    "channel_id": "550e8400-e29b-41d4-a716-446655440000",
    "external_ref": "msg-123456",
    "username": "john_doe",
    "message": "I'm feeling overwhelmed with the current project deadline."
  },
  {
    "channel_id": "550e8400-e29b-41d4-a716-446655440000",
    "external_ref": "msg-123457",
    "username": "jane_smith",
    "message": "Great work on the presentation today, team!"
  }
]
```

**Response (201 Created / 207 Multi-Status):**
```json
{
  "data": {
    "processed_messages": [
      {
        "message_id": "msg-uuid-1",
        "external_ref": "msg-123456",
        "status": "queued_for_analysis"
      },
      {
        "external_ref": "msg-123457",
        "status": "failed",
        "error": "User with username 'unknown_user' not found."
      }
    ],
    "summary": {
      "total_messages": 2,
      "successful": 1,
      "failed": 1
    }
  },
  "message": "Processed 1/2 messages successfully",
  "success": true,
  "timestamp": "2025-08-30T16:00:00Z"
}
```

**Message Processing Status:**
- `queued_for_analysis` - Successfully ingested, queued for ML analysis
- `failed` - Failed to process (with error details)

---

## 📈 Analytics Endpoints

### 1. Team Dashboard
**GET** `/analytics/team-dashboard/`

Get comprehensive team analytics for management dashboard.

**Query Parameters:**
- `start_date` (optional): ISO 8601 date (e.g., `2025-08-01T00:00:00Z`)
- `end_date` (optional): ISO 8601 date (e.g., `2025-08-30T23:59:59Z`)

**Default:** Last 30 days if no dates provided

**Response (200 OK):**
```json
{
  "data": {
    "period": {
      "start_date": "2025-08-01T00:00:00Z",
      "end_date": "2025-08-30T23:59:59Z",
      "calculated_at": "2025-08-30T16:00:00Z"
    },
    "team_overview": {
      "sentiment_weighted_avg": 0.65,
      "stress_weighted_avg": 0.32,
      "emotions": {
        "joy": 0.45,
        "sadness": 0.15,
        "anger": 0.08,
        "fear": 0.12,
        "love": 0.25,
        "surprise": 0.18
      },
      "message_count": 1247,
      "wellbeing_score": 7.2,
      "alert_level": "normal"
    },
    "user_analytics": [
      {
        "user_id": "user_001",
        "sentiment_weighted_avg": 0.72,
        "stress_weighted_avg": 0.28,
        "emotions": {
          "joy": 0.52,
          "sadness": 0.12,
          "anger": 0.05,
          "fear": 0.08,
          "love": 0.28,
          "surprise": 0.15
        },
        "message_count": 156,
        "wellbeing_score": 7.8,
        "trend": "improving",
        "alert_level": "normal"
      }
    ],
    "channel_analytics": [
      {
        "source": "discord",
        "sentiment_weighted_avg": 0.68,
        "stress_weighted_avg": 0.35,
        "emotions": {
          "joy": 0.42,
          "sadness": 0.18,
          "anger": 0.10,
          "fear": 0.15,
          "love": 0.22,
          "surprise": 0.20
        },
        "message_count": 523,
        "active_users": 15,
        "wellbeing_score": 6.9,
        "alert_level": "normal"
      }
    ],
    "trends": {},
    "alerts": []
  },
  "message": "Team analytics retrieved successfully",
  "success": true,
  "timestamp": "2025-08-30T16:00:00Z"
}
```

**Wellbeing Score:** 0-10 scale (0=Poor, 10=Excellent)
**Alert Levels:** `excellent`, `normal`, `warning`, `critical`
**Trends:** `improving`, `stable`, `declining`, `new`

### 2. User Wellbeing
**GET** `/analytics/user-wellbeing/`

Get individual user wellbeing data.

**Query Parameters:**
- `user_name` (required): Username to analyze
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date

**Response (200 OK):**
```json
{
  "user_name": "john_doe",
  "user_hash": "550e8400-e29b-41d4-a716-446655440000",
  "period": {
    "start_date": "2025-08-01T00:00:00Z",
    "end_date": "2025-08-30T23:59:59Z",
    "calculated_at": "2025-08-30T16:00:00Z"
  },
  "overall_metrics": {
    "sentiment_weighted_avg": 0.72,
    "stress_weighted_avg": 0.28,
    "emotions": {
      "joy": 0.52,
      "sadness": 0.12,
      "anger": 0.05,
      "fear": 0.08,
      "love": 0.28,
      "surprise": 0.15
    },
    "message_count": 156,
    "wellbeing_score": 7.8
  },
  "daily_trends": [
    {
      "date": "2025-08-30T00:00:00Z",
      "sentiment": 0.75,
      "stress": 0.25,
      "emotions": {
        "joy": 0.55,
        "sadness": 0.10,
        "anger": 0.05,
        "fear": 0.05,
        "love": 0.30,
        "surprise": 0.12
      },
      "message_count": 8,
      "wellbeing_score": 8.1
    }
  ],
  "channel_breakdown": [
    {
      "source": "discord",
      "sentiment": 0.78,
      "stress": 0.22,
      "emotions": {
        "joy": 0.58,
        "sadness": 0.08,
        "anger": 0.02,
        "fear": 0.05,
        "love": 0.32,
        "surprise": 0.18
      },
      "message_count": 89,
      "wellbeing_score": 8.3
    }
  ]
}
```

### 3. Channel Comparison
**GET** `/analytics/channel-comparison/`

Compare wellbeing metrics across different communication channels.

**Query Parameters:**
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date

**Default:** Last 7 days

**Response (200 OK):**
```json
{
  "period": {
    "start_date": "2025-08-23T00:00:00Z",
    "end_date": "2025-08-30T23:59:59Z"
  },
  "channel_stats": [
    {
      "source": "discord",
      "sentiment_avg": 0.68,
      "stress_avg": 0.35,
      "emotion_averages": {
        "joy": 0.42,
        "sadness": 0.18,
        "anger": 0.10,
        "fear": 0.15,
        "love": 0.22,
        "surprise": 0.20
      },
      "total_messages": 523,
      "active_users": 15,
      "wellbeing_score": 6.9
    },
    {
      "source": "meeting",
      "sentiment_avg": 0.72,
      "stress_avg": 0.28,
      "emotion_averages": {
        "joy": 0.38,
        "sadness": 0.12,
        "anger": 0.05,
        "fear": 0.18,
        "love": 0.15,
        "surprise": 0.25
      },
      "total_messages": 187,
      "active_users": 22,
      "wellbeing_score": 7.4
    }
  ]
}
```

### 4. Alerts
**GET** `/analytics/alerts/`

Get wellbeing alerts for users who may need attention.

**Query Parameters:**
- `severity` (optional): `critical`, `warning`, `all` (default: `all`)
- `limit` (optional): Number of alerts to return (default: 50)

**Response (200 OK):**
```json
{
  "data": {
    "alerts": [
      {
        "user_id": "user_005",
        "alert_type": "low_wellbeing",
        "severity": "critical",
        "wellbeing_score": 2.1,
        "stress_level": 0.89,
        "message": "User showing signs of severe stress and low wellbeing",
        "detected_at": "2025-08-30T14:30:00Z",
        "metrics": {
          "sentiment_avg": -0.65,
          "stress_avg": 0.89,
          "recent_message_count": 45
        }
      }
    ],
    "summary": {
      "total_alerts": 3,
      "critical": 1,
      "warning": 2
    }
  },
  "message": "Alerts retrieved successfully",
  "success": true
}
```

### 5. Wellbeing Trends
**GET** `/analytics/trends/`

Get wellbeing trends over time.

**Query Parameters:**
- `period` (optional): `daily`, `weekly`, `monthly` (default: `weekly`)
- `metric` (optional): `wellbeing_score`, `sentiment`, `stress`, `all` (default: `all`)
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date

**Response (200 OK):**
```json
{
  "data": {
    "period_type": "weekly",
    "metric": "wellbeing_score",
    "trends": [
      {
        "period_start": "2025-08-01T00:00:00Z",
        "period_end": "2025-08-07T23:59:59Z",
        "wellbeing_score": 6.8,
        "sentiment_avg": 0.62,
        "stress_avg": 0.38,
        "message_count": 234,
        "active_users": 18
      },
      {
        "period_start": "2025-08-08T00:00:00Z",
        "period_end": "2025-08-14T23:59:59Z",
        "wellbeing_score": 7.2,
        "sentiment_avg": 0.68,
        "stress_avg": 0.32,
        "message_count": 287,
        "active_users": 21
      }
    ],
    "analysis": {
      "trend_direction": "improving",
      "change_percentage": 5.9,
      "key_insights": [
        "Wellbeing scores have improved by 5.9% over the period",
        "Stress levels decreased while positive sentiment increased"
      ]
    }
  },
  "message": "Trends retrieved successfully",
  "success": true
}
```

---

## 🤖 Chatbot Endpoints

### 1. Chat with Bot
**POST** `/chatbot/chat/`

Send message to the emotional support chatbot.

**Authentication Required:** ✅

**Request Body:**
```json
{
  "message": "I'm feeling really stressed about the upcoming deadline",
  "conversation_id": 123
}
```

**Response (200 OK):**
```json
{
  "data": {
    "response": "I understand that deadlines can feel overwhelming. It's completely normal to feel stressed in these situations. Have you considered breaking down the tasks into smaller, manageable steps?",
    "conversation_id": 123,
    "emotions_detected": ["stress", "anxiety"],
    "crisis_level": "low",
    "support_suggestions": [
      "Take regular breaks",
      "Practice deep breathing exercises",
      "Consider speaking with your manager about workload"
    ]
  },
  "message": "Response generated successfully",
  "success": true,
  "timestamp": "2025-08-30T16:30:00Z"
}
```

### 2. Conversation List
**GET** `/chatbot/conversations/`

Get list of user's conversations with the chatbot.

**Authentication Required:** ✅

**Response (200 OK):**
```json
{
  "data": {
    "conversations": [
      {
        "id": 123,
        "title": "Stress Management Discussion",
        "status": "active",
        "created_at": "2025-08-30T10:00:00Z",
        "updated_at": "2025-08-30T16:30:00Z",
        "favourite": false,
        "archive": false,
        "follow_up_needed": true,
        "crisis_flags": 0,
        "last_message_preview": "I understand that deadlines can feel overwhelming..."
      }
    ],
    "total_count": 5,
    "active_conversations": 2
  },
  "message": "Conversations retrieved successfully",
  "success": true
}
```

### 3. Conversation History
**GET** `/chatbot/conversations/<conversation_id>/messages/`

Get message history for a specific conversation.

**Authentication Required:** ✅

**Response (200 OK):**
```json
{
  "data": {
    "conversation_id": 123,
    "messages": [
      {
        "id": 1,
        "content": "I'm feeling really stressed about the upcoming deadline",
        "is_from_user": true,
        "emotions": ["stress", "anxiety"],
        "crisis_level": "low",
        "support_request": false,
        "created_at": "2025-08-30T16:25:00Z"
      },
      {
        "id": 2,
        "content": "I understand that deadlines can feel overwhelming...",
        "is_from_user": false,
        "emotions": null,
        "crisis_level": "none",
        "support_request": false,
        "created_at": "2025-08-30T16:30:00Z"
      }
    ],
    "total_messages": 2
  },
  "message": "Conversation history retrieved successfully",
  "success": true
}
```

---

## 🛡️ Admin Endpoints

All admin endpoints are accessible through Django's admin interface:

**Admin URL:** `/admin/`

### Available Admin Models:
- **Users:** Manage user accounts, roles, and permissions
- **Channels:** View and manage communication channels
- **Messages:** View ingested messages and their analysis
- **Message Analysis:** View AI analysis results
- **Wellbeing Aggregates:** View calculated wellbeing metrics
- **Conversations:** View chatbot conversations
- **Chatbot Messages:** View individual chatbot interactions

---

## 🔍 Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_ERROR` | Authentication credentials invalid/missing |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `NOT_FOUND` | Requested resource not found |
| `INTERNAL_ERROR` | Server internal error |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

---

## 📝 Rate Limits

- **Authentication endpoints:** 5 requests per minute per IP
- **Message ingestion:** 100 requests per minute per user
- **Analytics endpoints:** 60 requests per minute per user
- **Chatbot endpoints:** 30 requests per minute per user

---

## 🚀 Getting Started

1. **Register** a new employee account using `/auth/register/`
2. **Login** to get access tokens using `/auth/login/`
3. **Create channels** for your communication platforms using `/channels/`
4. **Ingest messages** for analysis using `/messages/`
5. **View analytics** using various `/analytics/` endpoints
6. **Chat with the bot** for emotional support using `/chatbot/chat/`

---

## 📊 ML Analysis Features

The system automatically analyzes ingested messages for:

- **Sentiment Analysis:** Positive, negative, neutral sentiment detection
- **Emotion Detection:** Joy, sadness, anger, fear, love, surprise
- **Stress Level Detection:** Binary stress/no-stress classification with confidence scores
- **Wellbeing Scoring:** 0-10 composite wellbeing score
- **Trend Analysis:** Temporal wellbeing trend detection
- **Alert Generation:** Automatic alerts for users needing attention

All analysis happens asynchronously using Celery task queues for optimal performance.