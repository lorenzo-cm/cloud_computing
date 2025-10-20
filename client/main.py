import requests

response = requests.post("http://localhost:8000/api/recommend", json={"songs_seen": ["Yesterday - Remastered"]})

print(response.json())
