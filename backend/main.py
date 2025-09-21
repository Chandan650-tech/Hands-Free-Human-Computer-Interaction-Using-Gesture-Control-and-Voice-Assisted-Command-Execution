from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Hands-Free HCI API")

# ✅ whitelist: only safe commands allowed
WHITELIST = {
    "open_calculator": ["calc"] if os.name == "nt" else ["gnome-calculator"],
    "open_notepad": ["notepad"] if os.name == "nt" else ["gedit"]
}

class VoiceCommand(BaseModel):
    action: str

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/voice")
def voice_command(cmd: VoiceCommand):
    action = cmd.action.strip().lower()
    if action not in WHITELIST:
        raise HTTPException(status_code=400, detail="Action not allowed")
    # here you'd call subprocess.run(WHITELIST[action]) safely
    return {"status": "ok", "action": action}
