
import requests

url = "http://localhost:8001"
response = requests.get(url)
print(response.content)