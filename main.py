from datetime import datetime
from fastapi import FastAPI, Form
from fastapi.responses import Response, JSONResponse
from services.booking import handle_message
from data.db import get_booked_slots

app = FastAPI()

@app.get("/health")
async def health():
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        _ = get_booked_slots(today)
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/webhook")
async def webhook(From: str = Form(...), Body: str = Form(...)):
    user = From
    msg = Body.lower().strip()

    reply = handle_message(user, msg)

    return Response(
        content=f"<Response><Message>{reply}</Message></Response>",
        media_type="application/xml"
    )
