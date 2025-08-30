import requests
import json
import random

# API endpoint
MESSAGES_URL = "http://localhost:8000/api/messages/"

# Load users and channels from JSON files
with open("dummy_users.json", "r") as f:
    users = json.load(f)

with open("dummy_channels.json", "r") as f:
    channels = json.load(f)

# Sample meaningful messages for testing sentiment, stress, emotions
message_templates = [
    # Negative sentiment, stress=True, sadness
    "I'm feeling really down today, everything seems hopeless.",
    "This project is overwhelming, I can't handle the pressure anymore.",
    "Lost a close friend, my heart is broken.",
    # Positive sentiment, stress=False, joy
    "I aced the exam, I'm over the moon!",
    "The team outing was fantastic, had so much fun!",
    "Got promoted, couldn't be happier!",
    # Negative, stress=True, anger
    "This bug is infuriating, why won't it fix?",
    "The delays are unacceptable, I'm furious!",
    "Colleague's mistake ruined my work, so angry!",
    # Negative, stress=True, fear
    "Afraid I might lose my job, the market is tough.",
    "Nervous about the presentation tomorrow.",
    "Scared of the upcoming changes in the company.",
    # Positive, stress=False, love
    "I appreciate my team's support, love working here.",
    "Grateful for my family's love and care.",
    "Adore how collaborative everyone is.",
    # Neutral/Positive, stress=False, surprise
    "Wow, unexpected bonus this month!",
    "Surprised by the quick resolution of the issue.",
    "Didn't see that plot twist coming in the meeting.",
    # Mixed variations
    "Feeling neutral about the changes, but a bit anxious.",
    "Happy with the progress, but stressed about deadlines.",
    "Sad about leaving the team, but excited for new opportunities.",
    "Angry at the error, but relieved it's fixed.",
    "Fearful of failure, but determined to succeed.",
    "Joyful reunion with old friends.",
    "Loving the new office setup.",
    "Surprised by the positive feedback."
] * 5  # Repeat to have enough variations

# Generate 100 messages: distribute across users and channels
messages = []
for i in range(100):
    user = random.choice(users)
    channel = random.choice(channels)
    message_text = random.choice(message_templates) + f" (msg{i+1})"  # Add unique identifier
    external_ref = f"msg{i+1:03d}"
    messages.append({
        "channel_id": channel["channel_id"],
        "user_hash": user["user_hash"],
        "message": message_text,
        "external_ref": external_ref
    })

# Post messages
for msg in messages:
    response = requests.post(MESSAGES_URL, json=msg)
    if response.status_code == 201:
        print(f"Created message: {msg['external_ref']} for user {msg['user_hash']} in channel {msg['channel_id']}")
    else:
        print(f"Failed to create message {msg['external_ref']}: {response.text}")
        