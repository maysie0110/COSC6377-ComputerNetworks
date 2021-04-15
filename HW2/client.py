# https://www.kite.com/python/answers/how-to-make-a-request-with-a-user-agent-in-python

import requests

url = "http://127.0.0.1:8001"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

response = requests.get(url, headers=headers)
# print(response.content)