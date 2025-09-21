
# Backend (FastAPI)

## Run locally
```bash
cd backend
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

