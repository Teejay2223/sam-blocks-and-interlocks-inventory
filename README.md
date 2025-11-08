# SAM Blocks and Interlocks Inventory (Final Year Project)

> Short description: A web-based inventory system for SAM blocks and interlocks to help manage, track, and visualise components used in [project context].

Status: Draft / In development

University: [Your University Name]
Supervisor: [Supervisor Name]
Student: Teejay2223

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the app](#running-the-app)
  - [Locally (development)](#locally-development)
  - [Using Docker](#using-docker)
- [Testing](#testing)
- [Deployment notes](#deployment-notes)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Project Overview

This repository contains the source code and assets for the SAM Blocks and Interlocks Inventory — a final-year project that provides a web interface, data model, and tools to maintain an inventory of blocks and interlocks used in SAM systems. The application includes a backend (Python), frontend HTML templates, and deployment artifacts (Dockerfile, Procfile).

Add a short project abstract here describing aims, evaluation, and expected deliverables for the final year project.

## Features
- Add, edit, and remove inventory items (blocks and interlocks)
- Search and filter inventory
- Export/import data (CSV/JSON)
- Basic user roles (admin/viewer) — if implemented
- Deployment-ready (Dockerfile, Procfile)

## Tech stack
- Python (backend)
- HTML (frontend templates)
- Docker for containerisation
- Shell scripts for utility tasks

## Requirements
- Python 3.10+ (adjust as needed)
- pip
- Docker (optional, for containerised runs)

It is recommended to add a requirements.txt or a pyproject.toml listing the Python dependencies. If one does not exist yet, create it and pin the required packages.

## Installation

1. Clone the repository

```bash
git clone https://github.com/Teejay2223/sam-blocks-and-interlocks-inventory.git
cd sam-blocks-and-interlocks-inventory
```

2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
venv\Scripts\activate     # Windows (PowerShell)
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

If there is no requirements.txt yet, create one and include dependencies (Flask/Django/other frameworks, SQLAlchemy, etc.).

## Running the app

### Locally (development)

The exact command depends on the framework used (Flask, Django, FastAPI, etc.). Common examples:

- Flask

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

- Django

```bash
python manage.py migrate
python manage.py runserver
```

If you have a start script in the repository (e.g., app start or run.sh), use that instead. Update this README with the precise commands used by this project.

By default the app will be available at http://localhost:5000 (or another port depending on configuration).

### Using Docker

Build and run the container locally:

```bash
docker build -t sam-inventory .
docker run -p 8000:8000 sam-inventory
```

Adjust the exposed port to match your app configuration.

## Testing

Add project tests and document how to run them (e.g., pytest):

```bash
pytest
```

## Deployment notes

- The repository includes a Dockerfile and a Procfile. Configure your hosting provider (Heroku, Docker Hub, etc.) to build from the Dockerfile or use the Procfile as appropriate.
- Adding CI (GitHub Actions) to run linting and tests on push/PR is recommended.

## Contributing

As this is a final year project, contributions may be restricted. If you accept contributions, document how contributors should format commits, open issues, and submit pull requests.

Suggested basic rules:
- Open an issue describing the problem/feature first
- Create a branch named `feature/xxx` or `fix/xxx`
- Open a pull request against `main`

## License

Recommend adding a license (for example, MIT). If you want, I can add a LICENSE file with the chosen license text.

## Contact

Student: Teejay2223 (https://github.com/Teejay2223)

---

Notes for maintainer: please review and replace placeholder fields (University, Supervisor, exact run commands) and add a requirements.txt or pyproject.toml before merging.