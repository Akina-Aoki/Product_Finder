# Product_Finder

Event-driven product/inventory tracking system built with **Python 3.12**, **uv**, and Kafka.

This project is fully reproducible. All contributors use the same Python version and dependency lock file to ensure consistency across machines.

---

# 🧱 Tech Stack

- Python 3.12 (pinned)
- uv (dependency & environment management)
- Kafka (Docker)
- confluent-kafka
- Pydantic
- python-dotenv

---

# 📦 Prerequisites

Install uv if needed:

```bash
pip install uv
```

----
## First Time Set-up
1️⃣ Clone the Repository
```
git clone https://github.com/YOUR_USERNAME/Product_Finder.git
```

2️⃣ Install & Pin Python 3.12
In your VSCode/IDE
```
uv python install 3.12
uv python pin 3.12
```

Verify:
```
cat .python-version
```

Expected output:
```
3.12
```

3️⃣ Create Virtual Environment
```
uv venv
```

Activate it: Windows (Git Bash)
```
source .venv/Scripts/activate
```

Mac/Linux
```
source .venv/bin/activate
```

You should now see:
```
(Product_Finder)
```

4️⃣ Install Project Dependencies
- This installs all dependencies from uv.lock.
```
uv sync
```

- ⚠️ Do NOT use pip install.
- Always use for new dependencies.:
```
uv add <package>
```

5️⃣ Verify Environment Isolation

Check Python version:
```
python -V
```

Expected:
```
Python 3.12.x
```

Check interpreter path:
```
python -c "import sys; print(sys.executable)"
```

It must point to:
```
Product_Finder/.venv/...
```