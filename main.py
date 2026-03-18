from fastapi import FastAPI, Form
from fastapi.responses import Response
from services.booking import handle_message

app = FastAPI()

@app.post("/webhook")
async def webhook(From: str = Form(...), Body: str = Form(...)):
    user = From
    msg = Body.lower().strip()

    reply = handle_message(user, msg)

    return Response(
        content=f"<Response><Message>{reply}</Message></Response>",
        media_type="application/xml"
    )