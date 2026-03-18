import os
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

from contextlib import contextmanager

@contextmanager
def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def get_booked_slots(date):
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT slot FROM bookings WHERE booking_date=%s", (date,))
            return [row[0] for row in cursor.fetchall()]


def insert_booking(user, date, slot):
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO bookings (user_phone, booking_date, slot) VALUES (%s, %s, %s)",
                (user, date, slot)
            )
        conn.commit()
