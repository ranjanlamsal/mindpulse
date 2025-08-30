# MindPulse API Documentation

## Overview
MindPulse is an employee wellbeing analytics platform that analyzes messages from various channels (Discord, Meetings, Jira, Chat) to provide wellbeing insights.

## Base URL
```
http://localhost:8000/
```

## Data Structure Standards

### Wellbeing Score
- **Range**: 0-10 (higher is better)
- **10**: Excellent wellbeing
- **7-9**: Good wellbeing  
- **5-6**: Moderate wellbeing
- **3-4**: Poor wellbeing
- **0-2**: Critical wellbeing

### Alert Levels
- `excellent`: Wellbeing score > 7, low stress
- `normal`: Average wellbeing indicators
- `warning`: Wellbeing score < 5 or elevated stress
- `critical`: Wellbeing score < 3 or high stress

### Trend Indicators
- `improving`: Score increased > 5% from previous period
- `declining`: Score decreased > 5% from previous period
- `stable`: Within ±5% range
- `new`: No previous data available

---

## 🔐 Authentication APIs

### 1. User Signup
```http
POST /signup/
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@company.com",
  "password": "secure_password",
  "role": "employee"  // "employee", "manager", "admin"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "username": "john_doe"
}
```

### 2. User Login
```http
POST /login/
```

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "username": "john_doe",
  "role": "employee",
  "user_hash": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 📊 Data Ingestion APIs

### 3. Create Channel
```http
POST /channels/
```

**Request Body:**
```json
{
  "name": "General Chat",
  "type": "discord",  // "discord", "meeting", "jira", "chat"
  "external_id": "channel_12345",
  "is_active": true
}
```

### 4. Ingest Messages
```http
POST /messages/
```

**Single Message:**
```json
{
  "channel": {
    "name": "General Chat",
    "type": "discord",
    "external_id": "channel_12345"
  },
  "user_hash": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I'm feeling stressed about the deadline",
  "external_ref": "msg_67890"
}
```

**Batch Messages (for meetings):**
```json
[
  {
    "channel": {
      "name": "Team Standup",
      "type": "meeting",
      "external_id": "meet_123"
    },
    "user_hash": "user_uuid_1",
    "message": "I'm concerned about our progress",
    "external_ref": "meet_123_chunk_1"
  },
  {
    "channel": {
      "name": "Team Standup", 
      "type": "meeting",
      "external_id": "meet_123"
    },
    "user_hash": "user_uuid_2",
    "message": "Let's discuss solutions",
    "external_ref": "meet_123_chunk_2"
  }
]
```

---

## 📈 Analytics & Dashboard APIs

### 5. Team Dashboard (Main Management View)
```http
GET /analytics/team-dashboard/
```

**Query Parameters:**
- `start_date` (optional): ISO 8601 date (e.g., `2025-08-01T00:00:00Z`)
- `end_date` (optional): ISO 8601 date

**Response:**
```json
{
  "period": {
    "start_date": "2025-08-01T00:00:00Z",
    "end_date": "2025-08-30T23:59:59Z",
    "calculated_at": "2025-08-30T13:45:23Z"
  },
  "team_overview": {
    "sentiment_weighted_avg": 0.25,
    "stress_weighted_avg": 0.15,
    "emotions": {
      "joy": 0.35,
      "sadness": 0.20,
      "anger": 0.10,
      "fear": 0.12,
      "love": 0.18,
      "surprise": 0.05
    },
    "message_count": 1547,
    "wellbeing_score": 7.2,
    "alert_level": "normal"
  },
  "user_analytics": [
    {
      "user_id": "user_001",
      "sentiment_weighted_avg": 0.45,
      "stress_weighted_avg": 0.05,
      "emotions": {
        "joy": 0.60,
        "sadness": 0.10,
        "anger": 0.05,
        "fear": 0.05,
        "love": 0.15,
        "surprise": 0.05
      },
      "message_count": 23,
      "wellbeing_score": 8.5,
      "trend": "improving",
      "alert_level": "excellent"
    }
  ],
  "channel_analytics": [
    {
      "source": "discord",
      "sentiment_weighted_avg": 0.30,
      "stress_weighted_avg": 0.20,
      "emotions": {
        "joy": 0.40,
        "sadness": 0.25,
        "anger": 0.15,
        "fear": 0.10,
        "love": 0.08,
        "surprise": 0.02
      },
      "message_count": 456,
      "active_users": 12,
      "wellbeing_score": 6.8,
      "alert_level": "normal"
    }
  ],
  "alerts": [
    {
      "type": "critical_wellbeing",
      "severity": "high",
      "message": "2 employees showing critical wellbeing indicators",
      "count": 2,
      "action_required": true
    }
  ]
}
```

### 6. Individual User Wellbeing
```http
GET /analytics/user-wellbeing/?user_hash={user_hash}
```

**Response:**
```json
{
  "user_hash": "550e8400-e29b-41d4-a716-446655440000",
  "period": {
    "start_date": "2025-08-01T00:00:00Z",
    "end_date": "2025-08-30T23:59:59Z",
    "calculated_at": "2025-08-30T13:45:23Z"
  },
  "overall_metrics": {
    "sentiment_weighted_avg": 0.35,
    "stress_weighted_avg": 0.25,
    "emotions": {
      "joy": 0.40,
      "sadness": 0.20,
      "anger": 0.15,
      "fear": 0.10,
      "love": 0.12,
      "surprise": 0.03
    },
    "message_count": 145,
    "wellbeing_score": 6.8
  },
  "daily_trends": [
    {
      "date": "2025-08-29T00:00:00Z",
      "sentiment": 0.4,
      "stress": 0.2,
      "emotions": { "joy": 0.5, "sadness": 0.1, "anger": 0.05, "fear": 0.05, "love": 0.25, "surprise": 0.05 },
      "message_count": 12,
      "wellbeing_score": 7.2
    }
  ],
  "channel_breakdown": [
    {
      "source": "discord",
      "sentiment": 0.3,
      "stress": 0.3,
      "emotions": { "joy": 0.35, "sadness": 0.25, "anger": 0.20, "fear": 0.10, "love": 0.08, "surprise": 0.02 },
      "message_count": 89,
      "wellbeing_score": 6.2
    }
  ]
}
```

### 7. Channel Comparison
```http
GET /analytics/channel-comparison/
```

**Response:**
```json
{
  "period": {
    "start_date": "2025-08-24T00:00:00Z",
    "end_date": "2025-08-30T23:59:59Z",
    "calculated_at": "2025-08-30T13:45:23Z"
  },
  "channels": [
    {
      "source": "discord",
      "sentiment_weighted_avg": 0.30,
      "stress_weighted_avg": 0.20,
      "emotions": {
        "joy": 0.40,
        "sadness": 0.25,
        "anger": 0.15,
        "fear": 0.10,
        "love": 0.08,
        "surprise": 0.02
      },
      "total_messages": 456,
      "active_users": 12,
      "avg_messages_per_user": 38.0,
      "wellbeing_score": 6.8,
      "alert_level": "normal"
    },
    {
      "source": "meeting",
      "sentiment_weighted_avg": 0.20,
      "stress_weighted_avg": 0.10,
      "emotions": {
        "joy": 0.30,
        "sadness": 0.15,
        "anger": 0.08,
        "fear": 0.15,
        "love": 0.22,
        "surprise": 0.10
      },
      "total_messages": 89,
      "active_users": 8,
      "avg_messages_per_user": 11.1,
      "wellbeing_score": 7.5,
      "alert_level": "excellent"
    }
  ]
}
```

### 8. Alerts & Notifications
```http
GET /analytics/alerts/
```

**Response:**
```json
{
  "timestamp": "2025-08-30T13:45:23Z",
  "alerts": [
    {
      "type": "critical_wellbeing",
      "severity": "high",
      "message": "2 employees showing critical wellbeing indicators",
      "count": 2,
      "action_required": true
    },
    {
      "type": "elevated_stress",
      "severity": "medium",
      "message": "5 employees showing elevated stress levels",
      "count": 5,
      "action_required": false
    },
    {
      "type": "low_engagement",
      "severity": "medium",
      "message": "3 employees showing low communication engagement",
      "count": 3,
      "action_required": false
    }
  ],
  "summary": {
    "total_alerts": 3,
    "high_severity": 1,
    "medium_severity": 2,
    "requires_action": 1
  }
}
```

### 9. Wellbeing Trends
```http
GET /analytics/trends/?period=week|month|quarter
```

**Query Parameters:**
- `period`: `week` (7 days), `month` (30 days), `quarter` (90 days)

**Response:**
```json
{
  "period": "month",
  "interval": "day",
  "start_date": "2025-08-01T00:00:00Z",
  "end_date": "2025-08-30T23:59:59Z",
  "trends": [
    {
      "date": "2025-08-01T00:00:00Z",
      "sentiment": 0.25,
      "stress": 0.30,
      "emotions": {
        "joy": 0.35,
        "sadness": 0.25,
        "anger": 0.15,
        "fear": 0.12,
        "love": 0.10,
        "surprise": 0.03
      },
      "message_count": 234,
      "wellbeing_score": 6.2
    }
  ]
}
```

---

## 🎨 Frontend Implementation Guide

### Dashboard Components

#### 1. **Executive Summary Card**
```javascript
// Data source: /analytics/team-dashboard/
const summaryData = {
  wellbeingScore: 7.2,
  totalMessages: 1547,
  alertLevel: "normal",
  trend: "improving"
}
```

#### 2. **Team Wellbeing Gauge**
```javascript
// Circular gauge showing team wellbeing score (0-10)
const gaugeConfig = {
  value: teamOverview.wellbeing_score,
  min: 0,
  max: 10,
  colors: {
    critical: '#ff4444',  // 0-3
    warning: '#ffaa00',   // 3-5  
    normal: '#44aa44',    // 5-7
    excellent: '#00aa44'  // 7-10
  }
}
```

#### 3. **Emotion Radar Chart**
```javascript
// Data source: team_overview.emotions
const radarData = {
  labels: ['Joy', 'Love', 'Surprise', 'Sadness', 'Anger', 'Fear'],
  datasets: [{
    data: [emotions.joy, emotions.love, emotions.surprise, emotions.sadness, emotions.anger, emotions.fear]
  }]
}
```

#### 4. **Channel Comparison Bar Chart**
```javascript
// Data source: channel_analytics
const channelChart = {
  labels: channelAnalytics.map(c => c.source),
  datasets: [
    {
      label: 'Wellbeing Score',
      data: channelAnalytics.map(c => c.wellbeing_score),
      backgroundColor: channelAnalytics.map(c => getColorByAlertLevel(c.alert_level))
    }
  ]
}
```

#### 5. **User Distribution Histogram**
```javascript
// Data source: user_analytics
const distributionData = {
  excellent: userAnalytics.filter(u => u.wellbeing_score >= 7).length,
  good: userAnalytics.filter(u => u.wellbeing_score >= 5 && u.wellbeing_score < 7).length,
  poor: userAnalytics.filter(u => u.wellbeing_score >= 3 && u.wellbeing_score < 5).length,
  critical: userAnalytics.filter(u => u.wellbeing_score < 3).length
}
```

#### 6. **Trend Line Chart**
```javascript
// Data source: /analytics/trends/?period=month
const trendChart = {
  labels: trendsData.trends.map(t => new Date(t.date).toLocaleDateString()),
  datasets: [
    {
      label: 'Team Wellbeing',
      data: trendsData.trends.map(t => t.wellbeing_score),
      borderColor: '#007bff',
      fill: false
    }
  ]
}
```

#### 7. **Alert Panel**
```javascript
// Data source: /analytics/alerts/
const alertComponents = alerts.map(alert => ({
  type: alert.type,
  severity: alert.severity,
  message: alert.message,
  actionRequired: alert.action_required,
  color: getSeverityColor(alert.severity)
}))
```

### Color Schemes
```css
:root {
  --wellbeing-critical: #dc3545;
  --wellbeing-warning: #ffc107;
  --wellbeing-normal: #28a745;
  --wellbeing-excellent: #007bff;
  
  --emotion-joy: #ffd700;
  --emotion-love: #ff69b4;
  --emotion-surprise: #9370db;
  --emotion-sadness: #4682b4;
  --emotion-anger: #dc143c;
  --emotion-fear: #696969;
}
```

### Recommended Refresh Intervals
- **Team Dashboard**: 5 minutes
- **Alerts**: 2 minutes
- **Individual User Data**: 10 minutes
- **Trends**: 1 hour

---

## 🔧 Error Handling

All APIs return consistent error responses:

```json
{
  "error": "Error description",
  "details": "Additional error context (optional)"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized
- `403`: Forbidden (insufficient permissions)
- `500`: Internal Server Error

---

## 📝 Development Notes

1. **Date Formats**: All dates use ISO 8601 format with UTC timezone
2. **User Privacy**: User IDs are anonymized as `user_001`, `user_002`, etc.
3. **Real-time Updates**: Consider WebSocket integration for live dashboard updates
4. **Caching**: Analytics data is computed, consider caching for 5-10 minutes
5. **Pagination**: Not implemented yet, but recommended for user lists > 100 items