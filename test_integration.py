import requests

url = "http://127.0.0.1:8000/predict"

data = {
    "url": "http://paypal-login-security-update.tk",
    "user_id": 1
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())