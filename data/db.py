import os
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "Automation")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "problem")

from contextlib import contextmanager

@contextmanager
def get_conn():
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
    else:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
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
