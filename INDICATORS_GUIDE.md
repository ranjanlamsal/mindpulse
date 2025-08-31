# ML Indicators Guide for Frontend Development

## Overview
Your system uses 3 ML models to analyze messages and provide wellbeing insights. Here's what each indicator means and how to interpret the values.

## 1. Sentiment Analysis

### Values:
- **Label**: `"positive"` or `"negative"`
- **Score**: Float between 0.0 and 1.0

### Interpretation:
- **positive + high score (0.8-1.0)**: Very positive message (e.g., "I love working here!" = 0.989)
- **positive + low score (0.5-0.7)**: Mildly positive or neutral (e.g., "feeling neutral" = 0.955)
- **negative + high score (0.8-1.0)**: Very negative message (e.g., "I hate this project" = 0.992)
- **negative + low score (0.5-0.7)**: Mildly negative

### Frontend Usage:
```javascript
if (sentiment === 'positive' && sentiment_score > 0.8) {
    // Show green indicator - very positive
} else if (sentiment === 'positive') {
    // Show light green - mildly positive  
} else if (sentiment === 'negative' && sentiment_score > 0.8) {
    // Show red indicator - very negative
} else {
    // Show yellow - mildly negative
}
```

## 2. Emotion Detection

### Values:
- **Label**: `"sadness"`, `"joy"`, `"love"`, `"anger"`, `"fear"`, `"surprise"`
- **Score**: Float between 0.0 and 1.0 (confidence level)

### Interpretation:
- **joy**: Happy, excited, positive emotions
- **love**: Affection, appreciation, gratitude
- **sadness**: Sad, disappointed, down
- **anger**: Frustrated, angry, irritated
- **fear**: Worried, anxious, scared
- **surprise**: Unexpected, shocked, amazed

### Frontend Usage:
```javascript
const emotionColors = {
    'joy': '#22c55e',      // Green
    'love': '#ec4899',     // Pink  
    'sadness': '#3b82f6',  // Blue
    'anger': '#ef4444',    // Red
    'fear': '#f59e0b',     // Orange
    'surprise': '#8b5cf6'  // Purple
};

// Higher score = more confident detection
if (emotion_score > 0.7) {
    // Strong emotion detected
} else if (emotion_score > 0.4) {
    // Moderate emotion
} else {
    // Weak emotion signal
}
```

## 3. Stress Detection

### Values:
- **Label**: `true` (stressed) or `false` (not stressed)
- **Score**: Float between 0.0 and 1.0 (confidence level)

### Interpretation:
- **true + high score (0.8-1.0)**: Very confident stress detected
- **true + medium score (0.6-0.8)**: Moderate confidence stress
- **false + high score (0.8-1.0)**: Very confident NO stress
- **false + low score (0.5-0.7)**: Uncertain about stress level

### Frontend Usage:
```javascript
if (stress === true && stress_score > 0.8) {
    // Show red stress indicator - high confidence stress
    return { color: '#ef4444', level: 'high' };
} else if (stress === true && stress_score > 0.6) {
    // Show orange - moderate stress
    return { color: '#f59e0b', level: 'moderate' };
} else if (stress === false && stress_score > 0.8) {
    // Show green - confident no stress
    return { color: '#22c55e', level: 'low' };
} else {
    // Show gray - uncertain
    return { color: '#6b7280', level: 'unknown' };
}
```

## 4. Aggregated Scores (Analytics Dashboard)

### Sentiment Weighted Average:
- **Range**: -1.0 to +1.0
- **Calculation**: `(positive_scores - negative_scores) / total_messages`
- **Interpretation**:
  - `+0.5 to +1.0`: Very positive team sentiment
  - `+0.1 to +0.5`: Mildly positive
  - `-0.1 to +0.1`: Neutral
  - `-0.5 to -0.1`: Mildly negative  
  - `-1.0 to -0.5`: Very negative team sentiment

### Stress Weighted Average:
- **Range**: -1.0 to +1.0
- **Calculation**: `(stress_scores - no_stress_scores) / total_messages`
- **Interpretation**:
  - `+0.5 to +1.0`: High team stress levels
  - `+0.1 to +0.5`: Moderate stress
  - `-0.1 to +0.1`: Balanced stress levels
  - `-0.5 to -0.1`: Low stress levels
  - `-1.0 to -0.5`: Very low stress (relaxed team)

## 5. Example API Response Analysis

```json
{
  "user_message_analysis": {
    "sentiment": "negative",           // ← User is expressing negative sentiment
    "sentiment_score": 0.988,         // ← Very confident (98.8%) it's negative
    "emotion": "sadness",             // ← Primary emotion is sadness
    "emotion_score": 0.830,           // ← 83% confidence in sadness detection
    "stress_detected": true,          // ← Stress is present
    "stress_score": 0.996,            // ← Very confident (99.6%) stress detected
    "crisis_level": "low",            // ← Low crisis level
    "crisis_indicators": ["stressed"] // ← Specific stress keywords found
  }
}
```

### Frontend Interpretation:
- **Red alert**: Negative sentiment + high stress + sadness = user needs support
- **Show**: Stress indicator, negative sentiment badge, sadness emotion
- **Action**: Recommend wellbeing resources, check-in with manager

## 6. Dashboard Color Coding Recommendations

```javascript
// Sentiment colors
const getSentimentColor = (sentiment, score) => {
    if (sentiment === 'positive') {
        return score > 0.8 ? '#16a34a' : '#22c55e'; // Dark green / Green
    } else {
        return score > 0.8 ? '#dc2626' : '#ef4444'; // Dark red / Red
    }
};

// Stress level colors  
const getStressColor = (stressed, score) => {
    if (stressed && score > 0.8) return '#dc2626';  // High stress - Red
    if (stressed && score > 0.6) return '#f59e0b';  // Medium stress - Orange
    if (!stressed && score > 0.8) return '#16a34a'; // Low stress - Green
    return '#6b7280'; // Uncertain - Gray
};

// Wellbeing score colors (for aggregated data)
const getWellbeingColor = (score) => {
    if (score > 0.3) return '#16a34a';      // Good wellbeing - Green
    if (score > 0.0) return '#22c55e';      // Okay wellbeing - Light green
    if (score > -0.3) return '#f59e0b';     // Concerning - Orange
    return '#dc2626';                       // Poor wellbeing - Red
};
```

## Key Points for Frontend:
1. **Higher scores = more confident predictions**
2. **Sentiment**: positive/negative labels with confidence scores
3. **Stress**: true/false with confidence scores  
4. **Emotions**: 6 categories with confidence scores
5. **Aggregated data**: Uses weighted averages from -1 to +1
6. **Crisis levels**: none/low/moderate/high/critical for escalation