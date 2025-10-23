import requests

response = requests.post("http://localhost:8000/api/recommend", json={"songs": ["Back To Back"]})

print(response.json())
