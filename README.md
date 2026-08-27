# 🔎 Keynoculars

**A payment credential leak detector — finds exposed payment gateway API keys, verifies their risk, and checks git history for secrets thought to be deleted.**

## The Problem

Developers accidentally commit live payment gateway API keys to public code (GitHub repos, config files). Once exposed, these keys can be found and abused within minutes — enabling unauthorized refunds, fake payment links, and access to transaction data. Generic secret scanners (Gitleaks, TruffleHog, GitGuardian) catch secrets broadly, but aren't tuned for payment credentials specifically, and most don't explain what a leaked key can actually do.

## What Keynoculars Does

1. **Detects** payment-key-shaped strings in code using regex + Shannon entropy analysis
2. **Verifies** whether a found key is live, using a controlled sandbox (not live production accounts — strictly defense-only, no active exploitation)
3. **Checks git history** — catches secrets that were committed and later "deleted," but still recoverable from old commits
4. **Explains impact** — maps a key's type to what it can actually do (refunds, payment links, transaction reads), based on documented permission scopes, not live probing
5. **Reports honest metrics** — precision/recall on a labeled test set, including known limitations

## Architecture

Code/Repo Input → Regex + Entropy Detector → Verification Module → Git History Scanner → Impact Explainer → Dashboard (Streamlit)

## Results (25-sample labeled test set)

| Metric | Score |
|---|---|
| Precision | 0.83 |
| Recall | 1.00 |

**Honest limitation:** entropy-based detection can't always distinguish a truly random secret from a random-looking common password (e.g., flags `password123` as suspicious) — a known industry-wide tradeoff.

**Comparison note:** published benchmarks for Gitleaks (46% precision) and TruffleHog (6% precision) are on large real-world datasets; ours is on a small controlled set — included for context, not as a superiority claim.

## Why Not Just Use Gitleaks?

Keynoculars is a payment-credential specialist, not a generic scanner: tuned for payment key formats, adds git-history checking, explains real-world impact per key, and reports honest measured metrics.

## Tech Stack

Python, Flask (mock verification server), Streamlit (dashboard), regex + Shannon entropy

## Running It Locally

pip install -r requirements.txt
python mock_razorpay.py
python -m streamlit run dashboard.py

(run in two separate terminals)

## What Broke (and how we fixed it)

- Regex initially missed `SECRET_TOKEN=` and `secret_key:` formats — broadening it fixed recall but introduced a new false positive, a real precision/recall tradeoff we documented instead of hiding.
- `.gitignore` doesn't retroactively hide already-committed secrets — discovered by intentionally leaking a fake `.env` secret and testing it.
- Git-history scanning initially found nothing on Windows due to PowerShell's file encoding making Git see text files as binary — fixed by creating files via the editor instead of terminal echo.

## Future Work

GitHub App integration (OAuth + webhooks) for continuous scanning, pre-commit hook support, multi-provider expansion beyond Razorpay, larger real-world test dataset.

## Scope Note

Detection is tuned for Razorpay-style keys as the primary demonstration; the approach generalizes to other payment providers.

Save it, then run:

git add README.md requirements.txt
git commit -m "add README and requirements"
git push
