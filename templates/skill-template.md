---
name: <skill-name>
description: <short clear description of what this skill does>
category: <operational | development | infrastructure>
---

# Overview

Brief explanation of what this skill is about and why it matters.

---

# When to Use

Describe situations where this skill is useful.

Examples:

- When setting up a new LNbits instance
- When extending LNbits functionality
- When debugging issues

---

# Prerequisites

List required knowledge, tools, or setup.

- LNbits installed
- Basic Python knowledge
- Access to server / Docker
- API keys (if relevant)

---

# Inputs

What information is required to execute this skill?

Examples:

- Server IP or domain
- Wallet backend type
- Extension name
- Environment variables

---

# Steps

Clear, ordered instructions.

## Step 1: <title>

Explain what to do.

## Step 2: <title>

Explain next action.

## Step 3: <title>

Continue…

---

# Examples

Provide concrete examples.

## Example 1

```bash
docker run ...
```

## Example 2

```python
# sample code
```

---

# Expected Outcome

What should happen if everything works correctly?

* LNbits instance is running
* Extension appears in UI
* API returns expected response

---

# Common Pitfalls

List typical mistakes and how to avoid them.

* Misconfigured environment variables
* Wrong wallet backend
* Missing dependencies
* Permission issues

---

# Troubleshooting

Quick fixes for common issues.

* Check logs:

  ```bash
  docker logs lnbits
  ```

* Verify config:

  ```bash
  env | grep LNBITS
  ```

---

# Notes

Additional context, best practices, or warnings.

---

# References

Links to relevant resources:

* LNbits GitHub
* Official documentation
* Related skills in this repo

---

# Related Skills

Optional but useful for navigation.

* install-lnbits-docker
* configure-wallet-backend
* create-extension
