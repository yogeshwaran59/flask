import requests

url = "https://jsonplaceholder.typicode.com/users"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
