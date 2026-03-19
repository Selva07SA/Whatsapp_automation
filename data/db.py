import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

SHEET_WEBAPP_URL = os.getenv("SHEET_WEBAPP_URL")


def _post(payload):
    if not SHEET_WEBAPP_URL:
        raise RuntimeError("SHEET_WEBAPP_URL is not set")
    res = requests.post(
        SHEET_WEBAPP_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    res.raise_for_status()
    try:
        return res.json()
    except ValueError:
        # If Apps Script returns text/plain, try to parse JSON from text
        return requests.models.json.loads(res.text)


def get_booked_slots(date):
    data = _post({"action": "get_booked", "date": date})
    return data.get("booked", [])


def insert_booking(user, date, slot):
    data = _post({"action": "insert_booking", "user": user, "date": date, "slot": slot})
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "Unknown error"))
