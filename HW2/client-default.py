# https://www.kite.com/python/answers/how-to-make-a-request-with-a-user-agent-in-python
import requests

url = "http://127.0.0.1:8001"
response = requests.get(url)
# print(response.content)