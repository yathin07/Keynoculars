import requests

response = requests.post(
    "http://127.0.0.1:5000/v1/verify",
    json={"key_id": "rzp_test_DXJ29xk4Ff2qLm"}
)

print(response.json())