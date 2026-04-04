# ACEest Fitness App

## Overview

ACEest Fitness is a simple application for displaying workout and diet information.

---

## Local Setup & Execution

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aceest-fitness
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   _(If `requirements.txt` is not present, install dependencies manually as needed.)_

### Running the Application

```bash
python app.py
```

The app will start locally. Follow any console output for access instructions.

---

## Running Tests Manually

1. Ensure all dependencies are installed (see above).
2. Run the test suite:
   ```bash
   python -m unittest test_app.py
   ```
   or, if using pytest:
   ```bash
   pytest test_app.py
   ```
3. For coverage reports (if coverage is set up):
   ```bash
   coverage run -m unittest test_app.py
   coverage html
   open htmlcov/index.html
   ```

---

## CI/CD Integration

### Jenkins

- The `Jenkinsfile` defines the pipeline for automated build, test, and deployment.
- Typical stages include:
  - Checkout code
  - Install dependencies
  - Run tests
- Jenkins automates these steps on every push or pull request, ensuring code quality and deployment consistency.

### GitHub Actions

- GitHub Actions workflows (typically in `.github/workflows/`) automate similar steps:
  - On push or pull request, the workflow triggers
  - Installs dependencies
  - Runs tests
  - Build and package in docker container (if tests pass)
- Provides status checks directly in GitHub for fast feedback.

---
