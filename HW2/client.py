# import http.client

# conn = http.client.HTTPConnection("localhost",8000)
# conn.request("GET", "/")
# res = conn.getresponse()
# print(res.status, res.reason)

import requests

url = "http://localhost:8001"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

response = requests.get(url, headers=headers)
print(response.content)