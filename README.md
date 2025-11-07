# SAM Blocks and Interlocks Inventory

Final Year Project — Inventory system for SAM blocks and interlocks.

## Overview
This repository contains the SAM Blocks & Interlocks Inventory application, developed as a final year project. The system helps manage, track, and report on SAM blocks and interlocks used in maintenance and operations. It includes a Python backend, HTML frontend, and containerization support.

## Key features
- Register and manage SAM blocks and interlocks
- Search, filter, and export inventory lists
- **AI-Powered Block Detection**: Upload images to automatically detect and count blocks using computer vision
- Simple web UI (HTML + Python backend)
- Dockerfile and Procfile for deployment

## Project status
Under active development. The project contains core functionality and is being prepared for demonstration and evaluation as part of the final year project deliverables.

## Architecture
- Backend: Python (Flask or similar — see project files)
- Frontend: HTML templates + static assets
- Deployment: Dockerfile, Procfile for Heroku-like deployments

## Getting started (development)
Prerequisites:
- Python 3.9+
- pip
- Docker (optional, for containerized runs)

1. Clone the repo
```bash
git clone https://github.com/Teejay2223/sam-blocks-and-interlocks-inventory.git
cd sam-blocks-and-interlocks-inventory
```

2. Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
.venv\Scripts\activate     # Windows
# If you have requirements.txt
pip install -r requirements.txt
```

3. Run the app locally
```bash
# if the project uses Flask as an example
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

4. Open http://localhost:5000 in your browser.

## Docker (optional)
Build and run with Docker:
```bash
docker build -t sam-inventory:latest .
docker run -p 5000:5000 sam-inventory:latest
```

## File structure (high level)
- app/ or src/ — Python backend code
- templates/ — HTML templates
- static/ — CSS, JS, images
- Dockerfile — container definition
- Procfile — process declaration for PaaS

Adjust according to the actual layout in the repo.

## How to use (demo steps)
1. Add a new item: Navigate to Add Item and fill in details (serial, type, location, status).
2. Search: Use the search box to find items by serial or description.
3. Export: Export inventory to CSV for reporting.
4. **Block Detection**: Upload an image to automatically detect and count blocks (see [BLOCK_DETECTION.md](BLOCK_DETECTION.md) for details).

## For assessment (suggested contents to prepare)
- Short demo video (3–5 minutes) showing add/search/export/block-detection flows
- README with architecture and run instructions (this file)
- Documented test cases and expected results

## Contributing
This is primarily a final year project owned by @Teejay2223. Contributions are welcome but please open an issue first describing the change.

## License
No license file is included by default. If you want this project to be open-source, consider adding a LICENSE (e.g., MIT).

## Contact
Project owner: Teejay2223 — https://github.com/Teejay2223

---

If you want, I can:
- Tailor this README to match the exact file layout and framework in your repo (tell me which files are present or let me scan the repo),
- Add a requirements.txt or pyproject.toml,
- Create a simple GitHub Actions workflow for linting/testing, or
- Push this README directly to the repository (I will if you confirm).