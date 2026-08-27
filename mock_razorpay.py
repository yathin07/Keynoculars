from flask import Flask, jsonify, request

app = Flask(__name__)

# Pretend database of "real" keys that exist in our fake Razorpay
FAKE_VALID_KEYS = {
    "rzp_test_DXJ29xk4Ff2qLm": {
        "status": "active",
        "mode": "test",
        "capabilities": ["read_transactions", "issue_refunds", "create_payment_links"]
    }
}

@app.route("/v1/verify", methods=["POST"])
def verify_key():
    data = request.json
    key_id = data.get("key_id")

    if key_id in FAKE_VALID_KEYS:
        return jsonify({"found": True, **FAKE_VALID_KEYS[key_id]})
    else:
        return jsonify({"found": False})

if __name__ == "__main__":
    app.run(port=5000)