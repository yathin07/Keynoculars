import math
import re
from dataset import dataset

def shannon_entropy(s):
    if not s:
        return 0
    prob = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)

key_id_pattern = re.compile(r'rzp_(test|live)_[A-Za-z0-9]{10,}')
secret_line_pattern = re.compile(r'(?i)(secret|key)\w*\s*[:=]\s*[\'"]?(\S+?)[\'"]?$')
def predict(line):
    """Returns 1 if the line looks like it contains a secret, else 0."""
    if key_id_pattern.search(line):
        return 1

    match = secret_line_pattern.search(line)
    if match:
        value = match.group(2)
        entropy = shannon_entropy(value)
        if entropy > 3.0 and "(" not in value and ")" not in value:
            return 1

    return 0

true_positive = 0
false_positive = 0
true_negative = 0
false_negative = 0

for line, label in dataset:
    prediction = predict(line)

    if prediction == 1 and label == 1:
        true_positive += 1
    elif prediction == 1 and label == 0:
        false_positive += 1
        print(f"[FALSE POSITIVE] {line}")
    elif prediction == 0 and label == 1:
        false_negative += 1
        print(f"[FALSE NEGATIVE] {line}")
    elif prediction == 0 and label == 0:
        true_negative += 1

precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else 0
recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 0

print("\n--- Results ---")
print(f"True Positives: {true_positive}")
print(f"False Positives: {false_positive}")
print(f"True Negatives: {true_negative}")
print(f"False Negatives: {false_negative}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")