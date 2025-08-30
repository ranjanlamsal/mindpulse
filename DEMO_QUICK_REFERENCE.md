# 🎯 MindPulse Demo - Quick Reference

## 🚀 **What We've Built**

**MindPulse** is a comprehensive employee wellbeing analytics platform that transforms workplace communication into actionable mental health insights.

---

## 📊 **Core Features**

### ✅ **Real-time Message Analysis**
- **Discord Integration**: Live message ingestion from your Discord server
- **Meeting Transcripts**: Batch processing of meeting recordings
- **ML Analysis**: Sentiment, emotion (6 types), and stress detection
- **Multi-channel Support**: Discord, Meetings, Jira, Chat

### ✅ **Advanced Analytics**
- **Wellbeing Score**: 0-10 scale combining all metrics
- **Trend Analysis**: Daily/weekly/monthly patterns
- **Channel Comparison**: Platform-specific insights
- **User Anonymization**: Privacy-first manager dashboard

### ✅ **Management Dashboard**
- **Team Overview**: Aggregate wellbeing metrics
- **Individual Analytics**: Anonymous user insights  
- **Alert System**: Critical wellbeing notifications
- **Performance Tracking**: Channel and user trends

---

## 🔗 **Key API Endpoints**

| Purpose | Method | Endpoint | Description |
|---------|---------|----------|-------------|
| **Main Dashboard** | GET | `/analytics/team-dashboard/` | Complete management overview |
| **User Insights** | GET | `/analytics/user-wellbeing/?user_hash=X` | Individual wellbeing data |
| **Channel Analysis** | GET | `/analytics/channel-comparison/` | Platform performance comparison |
| **Alerts** | GET | `/analytics/alerts/` | Critical notifications |
| **Trends** | GET | `/analytics/trends/?period=month` | Historical patterns |
| **Message Ingestion** | POST | `/messages/` | Discord/Meeting data input |
| **Authentication** | POST | `/login/` & `/signup/` | User management |

---

## 📈 **Sample Dashboard Data**

### Team Overview Response
```json
{
  "team_overview": {
    "wellbeing_score": 7.2,           // 0-10 scale
    "sentiment_weighted_avg": 0.25,   // -1 to +1
    "stress_weighted_avg": 0.15,      // 0 to 1
    "emotions": {
      "joy": 0.35,
      "sadness": 0.20,
      "anger": 0.10,
      "fear": 0.12,
      "love": 0.18,
      "surprise": 0.05
    },
    "message_count": 1547,
    "alert_level": "normal"           // excellent|normal|warning|critical
  },
  "alerts": [
    {
      "type": "critical_wellbeing",
      "severity": "high",
      "message": "2 employees showing critical indicators",
      "action_required": true
    }
  ]
}
```

---

## 🎨 **Frontend Visualization Components**

### 1. **Executive Summary Card**
```javascript
Wellbeing Score: 7.2/10 ⬆️ +5%
Total Messages: 1,547
Alert Status: Normal ✅
```

### 2. **Team Health Gauge** 
- Circular gauge (0-10)
- Color-coded: Red(0-3), Orange(3-5), Green(5-7), Blue(7-10)

### 3. **Emotion Radar Chart**
- 6-point radar: Joy, Love, Surprise vs Sadness, Anger, Fear

### 4. **Channel Performance Bars**
- Discord: 6.8/10
- Meetings: 7.5/10  
- Jira: 5.2/10

### 5. **User Distribution Histogram**
- Excellent (7-10): 45% of users
- Good (5-7): 35% of users
- Poor (3-5): 15% of users
- Critical (0-3): 5% of users

### 6. **Trend Timeline**
- 30-day wellbeing score progression
- Identify patterns and interventions

---

## 🏗️ **Technical Architecture**

```
Discord Bot → POST /messages/ → ML Analysis → Wellbeing Aggregation → Dashboard APIs
                   ↓
Meeting Service → POST /messages/ → Async Processing → Daily Summaries → Manager Insights
```

**Key Technologies:**
- **Backend**: Django REST Framework
- **ML Models**: Custom sentiment/emotion/stress classifiers
- **Database**: SQLite (easily scalable to PostgreSQL)
- **Processing**: Celery for async ML analysis
- **Privacy**: UUID-based user anonymization

---

## 🚨 **Alert System**

### Alert Types:
- **Critical Wellbeing**: Score < 3, immediate attention required
- **Elevated Stress**: Stress levels > 50% for multiple users
- **Channel Performance**: Platforms showing poor metrics
- **Low Engagement**: Users with minimal communication

### Severity Levels:
- **High**: Requires immediate manager action
- **Medium**: Monitor and consider intervention
- **Low**: Informational, track trends

---

## 📱 **Demo Flow**

### 1. **Show Real Data**
```bash
curl "http://localhost:8000/analytics/team-dashboard/"
```

### 2. **Explain Wellbeing Score**
- Formula combines sentiment, stress, emotions
- Normalized to 0-10 scale for easy understanding
- Trends show intervention effectiveness

### 3. **Demonstrate Channel Insights**
```bash
curl "http://localhost:8000/analytics/channel-comparison/"
```

### 4. **Show Alert System**
```bash
curl "http://localhost:8000/analytics/alerts/"
```

### 5. **Individual Privacy**
```bash
curl "http://localhost:8000/analytics/user-wellbeing/?user_hash=XXXXX"
```

---

## 💡 **Business Value**

### **For HR/Management:**
- **Early Warning System**: Detect burnout before it becomes critical
- **Data-Driven Decisions**: Quantified wellbeing metrics
- **Channel Optimization**: Identify which platforms create stress
- **Intervention Tracking**: Measure policy effectiveness

### **For Employees:**
- **Self-Awareness**: Personal wellbeing trends
- **Privacy Protected**: Anonymized team insights
- **Proactive Support**: Early intervention opportunities

### **For Organizations:**
- **Retention**: Reduce turnover through wellbeing monitoring  
- **Productivity**: Happier employees perform better
- **Culture**: Data-driven wellbeing initiatives
- **Compliance**: Mental health duty of care

---

## 🎯 **Next Steps**

### **Immediate (Post-Demo):**
1. **Frontend Integration**: Connect React/Vue dashboard
2. **Real-time Updates**: WebSocket for live data
3. **User Authentication**: Secure role-based access

### **Short-term (1-2 weeks):**
1. **Slack Integration**: Expand beyond Discord
2. **Jira Integration**: Ticket analysis
3. **Email Notifications**: Alert system
4. **Export Features**: PDF reports

### **Long-term (1-3 months):**
1. **AI Recommendations**: Intervention suggestions
2. **Predictive Analytics**: Burnout risk modeling
3. **Mobile App**: Manager dashboard on-the-go
4. **Integration Hub**: Microsoft Teams, Zoom, etc.

---

## 🔧 **Quick Setup**

```bash
# Start the server
source ../env/bin/activate
python manage.py runserver

# Test the main dashboard
curl "http://localhost:8000/analytics/team-dashboard/"

# Your Discord server should be posting to:
# POST http://localhost:8000/messages/
```

**🎉 Ready for Demo!**