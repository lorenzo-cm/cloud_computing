import requests

response = requests.post("http://localhost:50017/api/recommend", json={"songs": ["Back To Back"]})

print(response.json())
