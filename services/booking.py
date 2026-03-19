import logging
from datetime import datetime, timedelta
from data.db import get_booked_slots, insert_booking
from utils.slots import get_available_slots, SLOTS
from services.state import *

logging.basicConfig(
    filename="turf-booking.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def normalize_user(user):
    if user.startswith("whatsapp:"):
        return user.split(":", 1)[1]
    return user


def format_menu(title, options):
    lines = [title, ""]
    for key, label in options:
        lines.append(f"[{key}] {label}")
    lines.append("")
    lines.append("Reply with the option number.")
    return "\n".join(lines)


def format_two_columns(options):
    if not options:
        return ""
    max_label = max(len(label) for _, label in options)
    col_width = max_label + 6
    lines = []
    for i in range(0, len(options), 2):
        left = options[i]
        right = options[i + 1] if i + 1 < len(options) else None
        left_text = f"[{left[0]}] {left[1]}"
        if right:
            right_text = f"[{right[0]}] {right[1]}"
            line = left_text.ljust(col_width) + right_text
        else:
            line = left_text
        lines.append(line)
    return "\n".join(lines)


def handle_message(user, msg):
    user = normalize_user(user)
    init_user(user)
    state = get_state(user)

    # START
    if state == "start":
        set_state(user, "date")
        return format_menu(
            "Welcome! Select date:",
            [("1", "Today"), ("2", "Tomorrow"), ("3", "Day After")]
        )

    # DATE
    elif state == "date":
        today = datetime.today()

        if msg == "1":
            date = today.strftime("%Y-%m-%d")
        elif msg == "2":
            date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif msg == "3":
            date = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            return format_menu(
                "Invalid option. Select date:",
                [("1", "Today"), ("2", "Tomorrow"), ("3", "Day After")]
            )

        set_data(user, "date", date)
        set_state(user, "slot")

        try:
            booked = get_booked_slots(date)
        except Exception:
            logging.exception("Failed to load booked slots. user=%s date=%s", user, date)
            reset_user(user)
            return "Sorry, couldn't load slots right now. Try again later."

        available = get_available_slots(booked)

        booked_text = "Booked: None" if not booked else "Booked:\n" + "\n".join(booked)

        if not available:
            reset_user(user)
            return f"Date: {date}\n{booked_text}\nNo slots available"

        slot_options = [(k, v) for k, v in available.items()]
        slots_block = format_two_columns(slot_options)
        return "\n".join([
            f"Date: {date}",
            booked_text,
            "",
            "Choose a slot:",
            slots_block,
            "",
            "Reply with the option number."
        ])

    # SLOT
    elif state == "slot":
        if msg == "0":
            set_state(user, "date")
            return format_menu(
                "Select date:",
                [("1", "Today"), ("2", "Tomorrow"), ("3", "Day After")]
            )

        if msg not in SLOTS:
            return "Choose valid slot (1-10)."

        date = get_data(user, "date")
        try:
            booked = get_booked_slots(date)
        except Exception:
            logging.exception("Failed to load booked slots. user=%s date=%s", user, date)
            reset_user(user)
            return "Sorry, couldn't load slots right now. Try again later."

        slot = SLOTS[msg]
        if slot in booked:
            return "That slot was just booked. Please choose another slot."

        set_data(user, "slot", slot)

        otp = generate_otp(user)
        set_state(user, "otp")

        return f"Enter OTP (valid for {OTP_TTL_MINUTES} minutes):\n{otp}"

    # OTP
    elif state == "otp":
        if otp_expired(user):
            set_state(user, "slot")
            return "OTP expired. Please choose your slot again."

        if verify_otp(user, msg):
            date = get_data(user, "date")
            slot = get_data(user, "slot")

            try:
                booked = get_booked_slots(date)
            except Exception:
                logging.exception("Failed to load booked slots. user=%s date=%s", user, date)
                reset_user(user)
                return "Sorry, couldn't load slots right now. Try again later."

            if slot in booked:
                reset_user(user)
                return "That slot was already booked. Please start again and choose another slot."

            try:
                insert_booking(user, date, slot)
            except Exception:
                logging.exception("Booking insert failed. user=%s date=%s slot=%s", user, date, slot)
                return "We couldn't confirm your booking due to a server error. Please send the OTP again to retry."

            reset_user(user)
            return f"Booking Confirmed\nDate: {date}\nTime: {slot}"

        else:
            attempts = increment_attempt(user)

            if attempts >= 3:
                reset_user(user)
                return "Too many wrong attempts. Start again."

            return f"Invalid OTP\nAttempts left: {3 - attempts}"

    return "Send 'book turf'"
