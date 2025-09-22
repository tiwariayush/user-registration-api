from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict

app = FastAPI(title="Mock Mailer Service")

class MailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str

_last: Dict[str, str] = {}

@app.post("/send", status_code=202)
def send_mail(req: MailRequest):
    # Pretend to send mail and store last code by recipient for tests
    try:
        code = req.body.strip().split(":")[-1].strip()
        if len(code) == 4 and code.isdigit():
            _last[req.to] = code
    except Exception:
        pass
    return {"status": "accepted"}

@app.get("/__last_code")
def last_code(email: EmailStr):
    code = _last.get(email)
    if not code:
        raise HTTPException(status_code=404, detail="No code")
    return {"email": email, "code": code}
