import requests

response = requests.post("http://127.0.0.1:3000/api/search", json={"query": ""})
print(response.json())
