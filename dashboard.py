import streamlit as st
import os
import re
import math
import requests

def shannon_entropy(s):
    if not s:
        return 0
    prob = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)

key_id_pattern = re.compile(r'rzp_(test|live)_[A-Za-z0-9]{10,}')
secret_line_pattern = re.compile(r'(?i)(secret|key)\w*\s*[:=]\s*[\'"]?(\S+?)[\'"]?$')

def verify_key(key_id):
    try:
        response = requests.post("http://127.0.0.1:5000/v1/verify", json={"key_id": key_id}, timeout=2)
        return response.json()
    except requests.exceptions.RequestException:
        return {"found": False}

def scan_folder(folder):
    rows = []
    IGNORE_FILES = {"dashboard.py", "detect.py", "mock_razorpay.py", "test_verify.py", "evaluate.py", "dataset.py"}
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith((".py", ".txt", ".env", ".js", ".json", ".yml")):
                filepath = os.path.join(root, filename)
                with open(filepath, "r", errors="ignore") as f:
                    for line in f:
                        for match in key_id_pattern.finditer(line):
                            key = match.group()
                            v = verify_key(key)
                            status = v.get("status", "unknown") if v.get("found") else "not verified"
                            rows.append({"Type": "KEY_ID", "File": filepath, "Value": key, "Status": status})
                        for match in secret_line_pattern.finditer(line):
                            value = match.group(2)
                            entropy = shannon_entropy(value)
                            if entropy > 3.0 and "(" not in value and ")" not in value:
                                rows.append({"Type": "SECRET", "File": filepath, "Value": value, "Status": f"entropy {entropy:.2f}"})
    return rows

st.title("🔎 Keynoculars")
st.write("Payment credential leak detector")

folder = st.text_input("Folder to scan", value=".")

if st.button("Scan"):
    results = scan_folder(folder)
    if results:
        st.write(f"Found {len(results)} item(s):")
        st.table(results)
    else:
        st.success("No leaks found.")