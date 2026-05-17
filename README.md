# Autonomous Insurance Claims Processing Agent

An AI-powered FNOL (First Notice of Loss) document processing system that extracts fields, validates data, and routes claims automatically.

---

## Project Structure

```
insurance_agent/
├── backend/
│   ├── app.py            # Flask REST API
│   ├── agent.py          # Orchestration logic
│   ├── extractor.py      # Field extraction (regex-based)
│   ├── validator.py      # Missing & inconsistency checks
│   ├── router.py         # Routing rules engine
│   └── requirements.txt  # Python dependencies
└── frontend/
    └── index.html        # Single-file HTML/CSS/JS UI
```

---

## Prerequisites

- **Python 3.9 or higher**
- **pip** (Python package manager)
- A modern web browser (Chrome, Firefox, Edge)

---

## Setup & Run Instructions

### Step 1 — Clone / Extract the Project

Extract the zip file to a folder of your choice. Open a terminal and navigate inside:

```bash
cd insurance_agent
```

---

### Step 2 — Set Up the Python Backend

#### Create a virtual environment (recommended)

```bash
# Create venv
python -m venv venv

# Activate (macOS / Linux)
source venv/bin/activate

# Activate (Windows CMD)
venv\Scripts\activate

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1
```

#### Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `flask` — Web framework
- `flask-cors` — Allows the frontend to call the backend
- `pdfplumber` — Extracts text from PDF files

---

### Step 3 — Start the Flask Backend

From inside the `backend/` folder, run:

```bash
python app.py
```

You should see output like:

```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

**Leave this terminal window open.** The backend must be running while you use the app.

---

### Step 4 — Open the Frontend

Open a **new terminal** (or a file explorer window) and navigate to the `frontend/` folder.

**Option A — Direct file open (simplest)**
```
Double-click frontend/index.html in your file explorer
```

**Option B — Using Python's HTTP server (recommended)**
```bash
cd frontend
python -m http.server 8080
```
Then open `http://localhost:8080` in your browser.

> **Note:** The frontend connects to `http://localhost:5000` for the backend API.

---

### Step 5 — Use the Application

1. Click **"Drop FNOL Document"** or drag and drop a `.pdf` or `.txt` file.
2. Click **"⚡ Process Claim"**.
3. View results across four tabs:
   - **Extracted Fields** — All parsed policy, incident, asset, and party data
   - **Issues** — Missing mandatory fields + consistency warnings
   - **Reasoning** — Human-readable explanation of the routing decision
   - **JSON** — Full raw output in JSON format (copyable)

---

## Routing Logic

| Rule | Route |
|------|-------|
| Estimated damage < ₹25,000 AND no missing fields AND no flags | **Fast-Track** |
| Any mandatory field is missing | **Manual Review** |
| Description contains: `fraud`, `staged`, `inconsistent`, `suspicious`, etc. | **Investigation Flag** |
| Claim type = `injury` | **Specialist Queue** |
| Damage ≥ ₹25,000 with all fields present | **Standard Review** |

> Priority order: Investigation Flag > Specialist Queue > Manual Review > Standard Review > Fast-Track

---

## Mandatory Fields Checked

- Policy Number
- Policyholder Name
- Incident Date
- Incident Location
- Incident Description
- Claimant Name
- Asset Type
- Estimated Damage
- Claim Type
- Initial Estimate

---

## API Reference

### POST `/process`

Upload a FNOL document for processing.

**Request:** `multipart/form-data` with field `file` (.pdf or .txt)

**Response:**
```json
{
  "extractedFields": {
    "policyNumber": "AUTO-2024-78432",
    "policyholderName": "Ramesh Kumar",
    "effectiveDateStart": "2024-04-01",
    "effectiveDateEnd": "2025-03-31",
    "incidentDate": "2024-11-15",
    "incidentTime": "09:30 AM",
    "incidentLocation": "MG Road, Bengaluru",
    "incidentDescription": "Rear-end collision at traffic signal...",
    "claimantName": "Ramesh Kumar",
    "thirdParties": "Vikram Singh",
    "contactDetails": "+91-9876543210",
    "assetType": "Private Motor Vehicle",
    "assetId": "KA05CD6789",
    "estimatedDamage": 18000.0,
    "claimType": "vehicle_damage",
    "attachments": "Photos of damage (3 images), FIR Copy",
    "initialEstimate": 18000.0
  },
  "missingFields": [],
  "warnings": [],
  "recommendedRoute": "Fast-Track",
  "reasoning": "Estimated damage (18000.00) is below threshold of 25,000..."
}
```

### GET `/health`

Returns `{"status": "ok"}` to confirm the server is running.

---

## Tech Stack

- **Backend:** Python 3.9+, Flask, pdfplumber
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (no frameworks)
- **Extraction:** Regex-based pattern matching
- **Communication:** REST API with JSON responses

---
## Demo link
https://drive.google.com/file/d/1a5RWzN2toJQfOt6zXWIKe3_FrlnEAazU/view?usp=sharing
