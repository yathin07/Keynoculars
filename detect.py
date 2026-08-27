import re
import math
import os
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
        response = requests.post(
            "http://127.0.0.1:5000/v1/verify",
            json={"key_id": key_id},
            timeout=2
        )
        return response.json()
    except requests.exceptions.RequestException:
        return {"found": False, "error": "server unreachable"}

def scan_file(filepath):
    results = []
    with open(filepath, "r", errors="ignore") as f:
        lines = f.readlines()

    for line in lines:
        for match in key_id_pattern.finditer(line):
            key = match.group()
            verify_result = verify_key(key)

            if verify_result.get("found"):
                status = verify_result["status"]
                caps = ", ".join(verify_result["capabilities"])
                results.append(f"[KEY_ID - LIVE] {filepath}: {key} | Status: {status} | Can do: {caps}")
            else:
                results.append(f"[KEY_ID - UNKNOWN] {filepath}: {key} | Not found in verification system")

        for match in secret_line_pattern.finditer(line):
            value = match.group(2)
            entropy = shannon_entropy(value)
            if entropy > 3.0 and "(" not in value and ")" not in value:
                results.append(f"[SECRET] {filepath}: {value}  |  Entropy: {entropy:.2f}")

    return results

def scan_folder(folder):
    all_results = []
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith((".py", ".txt", ".env", ".js", ".json", ".yml")):
                filepath = os.path.join(root, filename)
                all_results.extend(scan_file(filepath))
    return all_results
import subprocess

def scan_git_history(repo_path):
    results = []
    output = subprocess.run(
        ["git", "-C", repo_path, "log", "-p", "--all"],
        capture_output=True, text=True, errors="ignore"
    ).stdout

    for match in key_id_pattern.finditer(output):
        key = match.group()
        results.append(f"[HISTORICAL KEY_ID] {repo_path}: {key}")

    for match in secret_line_pattern.finditer(output):
        value = match.group(2)
        entropy = shannon_entropy(value)
        if entropy > 3.0 and "(" not in value and ")" not in value:
            results.append(f"[HISTORICAL SECRET] {repo_path}: {value} | Entropy: {entropy:.2f}")

    return results

print("--- Scan Results ---")
for r in scan_folder("."):
    print(r)
print("\n--- Git History Scan (demo_leak_repo2) ---")
for r in scan_git_history("demo_leak_repo2"):
    print(r)