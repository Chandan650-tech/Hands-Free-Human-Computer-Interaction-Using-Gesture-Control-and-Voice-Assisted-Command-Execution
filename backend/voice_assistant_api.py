from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import random
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import re

import pywhatkit as kit  # WhatsApp integration

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEATHER_API_KEY = "68b21dc65d944d1ca70175305252606"
timers = {}

# === Your contact book ===
CONTACTS = {
    "atul": {"email": "atulkumar162625@gmail.com", "phone": "+917019624752"},
    "manoj": {"email": "jane@example.com", "phone": "+918618762596"},
    "amma": {"email": None, "phone": "+918746940856"},
    "charan": {"email": "charanreddy6426@gmail.com", "phone": "+916301492067"},
    "vishal": {"email": None, "phone": "+919620413854"},
}

# ---------------------------
# Utilities
# ---------------------------
def normalize_name(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

def resolve_contact(name: str):
    if not name:
        return None
    key = normalize_name(name)
    if key in CONTACTS:
        return CONTACTS[key], key
    for k in CONTACTS:
        if key in k or k in key:
            return CONTACTS[k], k
    return None

def send_email(to_email: str, subject: str, body: str):
    sender = "chandanm0357@gmail.com"
    password = "npfs plth rupb tixz"  # your Gmail app password

    # Fallbacks
    if not subject and body:
        subject = body[:30] + "..." if len(body) > 30 else body
    if not body:
        body = "(No message provided)"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True, "✅ Email sent successfully."
    except Exception as e:
        return False, f"❌ Email failed: {e}"

def send_whatsapp(phone: str, message: str):
    try:
        if not message:
            message = "(No message provided)"

        # Send instantly without scheduling
        kit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True, close_time=30)
        return True, "✅ WhatsApp message sent successfully."
    except Exception as e:
        return False, f"❌ WhatsApp failed: {e}"

# ---------------------------
# NLP Parser
# ---------------------------
def parse_intent(raw: str):
    text = raw.strip().lower()
    is_email = any(w in text for w in ["email", "mail"])
    is_wa = any(w in text for w in ["whatsapp", "send message", "message on whatsapp"])

    if not (is_email or is_wa):
        return {"intent": "other"}

    channel = "email" if is_email and not is_wa else ("whatsapp" if is_wa and not is_email else None)

    recip = None
    m = re.search(r"\bto\s+([a-zA-Z ]+?)(?:\b(on|about|saying|that|subject|body|:)|$)", text)
    if m:
        recip = m.group(1)
    else:
        m2 = re.search(r"\b(email|mail|message|whatsapp)\s+([a-zA-Z ]+?)(?:\b(on|about|saying|that|subject|body|:)|$)", text)
        if m2:
            recip = m2.group(2)
        else:
            m3 = re.search(r"\bto\s+([a-zA-Z ]+):", text)
            if m3:
                recip = m3.group(1)

    recip = recip.strip() if recip else None

    subject = None
    body = None

    m_sub_body = re.search(r"subject\s+(.+?)\s+body\s+(.+)$", text)
    if m_sub_body:
        subject = m_sub_body.group(1).strip(" :-")
        body = m_sub_body.group(2).strip()
    else:
        m_about = re.search(r"\babout\s+(.+?)(?:\s*[-–:]\s*|\s+saying\s+)(.+)$", text)
        if m_about:
            subject = m_about.group(1).strip()
            body = m_about.group(2).strip()
        else:
            m_say = re.search(r"\b(saying|that)\s+(.+)$", text)
            if m_say:
                body = m_say.group(2).strip()
            else:
                m_colon = re.search(r":\s*(.+)$", text)
                if m_colon:
                    body = m_colon.group(1).strip()

    if not subject and channel == "email" and body:
        subject = body.split(".")[0][:60].strip()

    # Fallback: if no body but recipient only, treat remainder as body
    if not body and recip:
        body = text.replace(recip, "").replace("email", "").replace("whatsapp", "").strip()

    return {
        "intent": "send_message",
        "channel": channel,
        "recipient": recip,
        "subject": subject,
        "body": body,
    }

# ---------------------------
# Core routes
# ---------------------------
@app.get("/")
def root():
    return {"message": "Proton Voice Assistant (with email & WhatsApp fixes) running."}

@app.post("/voice-command")
async def handle_voice_command(request: Request):
    data = await request.json()
    command = data.get("command", "")
    text = command.strip()
    print(f"🧠 Received: {text}")

    parsed = parse_intent(text)

    if parsed.get("intent") == "send_message":
        channel = parsed.get("channel")
        recip_str = parsed.get("recipient")
        subject = parsed.get("subject")
        body = parsed.get("body")

        if not channel:
            return {"response": "Should I send an email or a WhatsApp message?"}

        resolved = resolve_contact(recip_str) if recip_str else None
        if not resolved:
            return {"response": "Who should I send it to? (say a saved contact name)"}
        contact, contact_key = resolved

        if channel == "email":
            if not contact.get("email"):
                return {"response": f"I don't have an email for {contact_key}. Add one to contacts."}
            ok, msg = send_email(contact["email"], subject or "", body or "")
            return {"response": msg}

        if channel == "whatsapp":
            if not contact.get("phone"):
                return {"response": f"I don't have a phone number for {contact_key}. Add one to contacts."}
            ok, msg = send_whatsapp(contact["phone"], body or subject or "")
            return {"response": msg}

        return {"response": "I couldn't determine the channel to use."}

    # ---------------- Other features (gesture, search, weather, etc.) ----------------
    low = text.lower()
    # Gesture commands
    if "launch" in low and "gesture" in low:
        try:
            requests.get("http://localhost:8000/start")
            return {"response": "Launching gesture recognition."}
        except:
            return {"response": "Unable to connect to gesture system."}

    if "stop" in low and "gesture" in low:
        try:
            requests.get("http://localhost:8000/stop")
            return {"response": "Stopping gesture recognition."}
        except:
            return {"response": "Could not stop gesture recognition."}

    # Search
    if "search" in low:
        q = low.replace("search", "").strip()
        if q:
            url = f"https://www.google.com/search?q={q.replace(' ', '+')}"
            return {"response": f"Here are results for {q}", "url": url}
        return {"response": "What should I search for?"}

    # Maps
    if "map" in low or "location" in low:
        loc = low.replace("map", "").replace("location", "").strip()
        if loc:
            url = f"https://www.google.com/maps/search/{loc.replace(' ', '+')}"
            return {"response": f"Showing map for {loc}", "url": url}
        return {"response": "Please specify a location to search."}

    # Date/time
    if "date" in low or "time" in low:
        now = datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
        return {"response": f"Current date and time is {now}"}

    # Clipboard
    if "copy" in low:
        import pyautogui
        pyautogui.hotkey('ctrl', 'c')
        return {"response": "Copied to clipboard."}

    if "paste" in low:
        import pyautogui
        pyautogui.hotkey('ctrl', 'v')
        return {"response": "Pasted from clipboard."}

    # Small talk
    if "joke" in low:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the computer go to the doctor? It had a virus!",
            "I'm reading a book on anti-gravity. It's impossible to put down!",
        ]
        return {"response": random.choice(jokes)}

    if "weather in" in low:
        city = low.split("weather in")[-1].strip()
        if city:
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            )
            if r.status_code == 200:
                d = r.json()
                temp = d["main"]["temp"]
                desc = d["weather"][0]["description"]
                return {"response": f"The weather in {city} is {desc} with {temp}°C."}
            return {"response": f"Sorry, I couldn't find the weather for {city}."}
        return {"response": "Please specify a city for the weather report."}

    if "set timer for" in low:
        m = re.search(r"set timer for (\d+)\s*(seconds|minutes)", low)
        if m:
            n = int(m.group(1)); unit = m.group(2)
            seconds = n * 60 if unit == "minutes" else n
            timer_id = str(time.time())
            threading.Thread(target=timer_countdown, args=(timer_id, seconds), daemon=True).start()
            return {"response": f"Timer set for {n} {unit}."}
        return {"response": "Please specify a valid timer duration."}

    if "how are you" in low:
        return {"response": random.choice(["I'm great, thanks!", "Feeling awesome — how can I help?", "Ready to assist!"])}

    if "who created you" in low:
        return {"response": "I was created by an amazing developer like Chandan!"}

    if "tell me about yourself" in low:
        return {"response": "I'm Proton — I help with gestures, search, weather, email, WhatsApp and more."}

    return {"response": "Sorry, I didn't understand that command."}

# ---------------------------
# Timer helper
# ---------------------------
def timer_countdown(timer_id, seconds):
    time.sleep(seconds)
    print(f"⏰ Timer {timer_id} finished!")

