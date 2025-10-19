import requests

response = requests.get("http://localhost:8000/api/recommend", params={"songs_seen": ["song1", "song2"]})

print(response.json())