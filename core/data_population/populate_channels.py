import requests
import json

# API endpoint
CHANNELS_URL = "http://localhost:8000/api/channel/"

# Generate 10 channels: 4 discord, 3 meeting, 3 jira
channels = [
    {"name": f"Discord_Channel_{i}", "type": "discord", "external_id": f"EXT_D{i:03d}"}
    for i in range(1, 5)
] + [
    {"name": f"Meeting_Channel_{i}", "type": "meeting", "external_id": f"EXT_M{i:03d}"}
    for i in range(1, 4)
] + [
    {"name": f"Jira_Channel_{i}", "type": "jira", "external_id": f"EXT_J{i:03d}"}
    for i in range(1, 4)
]

# Store channel IDs
channel_data = []

# Create channels
for channel in channels:
    response = requests.post(CHANNELS_URL, json=channel)
    if response.status_code == 200:
        data = response.json().get("data")
        channel_data.append({
            "name": channel["name"],
            "type": channel["type"],
            "channel_id": data["id"]
        })
        print(f"Created channel: {channel['name']} ({channel['type']}) - ID: {data['id']}")
    else:
        print(f"Failed to create channel {channel['name']}: {response.text}")

# Output channel data
print("\nChannel Data:")
print(json.dumps(channel_data, indent=2))