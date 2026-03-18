import os
import random
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; env vars can be set by system
    pass

user_state = {}
user_data = {}
otp_store = {}
otp_meta = {}

OTP_TTL_MINUTES = int(os.getenv("OTP_TTL_MINUTES", "5"))

def init_user(user):
    if user not in user_state:
        user_state[user] = "start"
        user_data[user] = {}


def set_state(user, state):
    user_state[user] = state


def get_state(user):
    return user_state.get(user)


def set_data(user, key, value):
    user_data[user][key] = value


def get_data(user, key):
    return user_data[user].get(key)


def reset_user(user):
    user_state.pop(user, None)
    user_data.pop(user, None)
    otp_store.pop(user, None)
    otp_meta.pop(user, None)

# OTP

def generate_otp(user):
    otp = str(random.randint(1000, 9999))
    otp_store[user] = otp
    otp_meta[user] = {
        "created_at": datetime.utcnow(),
        "attempts": 0
    }
    return otp


def _otp_expired(user):
    meta = otp_meta.get(user)
    if not meta:
        return True
    return datetime.utcnow() - meta["created_at"] > timedelta(minutes=OTP_TTL_MINUTES)


def verify_otp(user, otp):
    if _otp_expired(user):
        return False
    return otp_store.get(user) == otp


def increment_attempt(user):
    meta = otp_meta.get(user)
    if not meta:
        otp_meta[user] = {"created_at": datetime.utcnow(), "attempts": 0}
        meta = otp_meta[user]
    meta["attempts"] += 1
    return meta["attempts"]


def otp_expired(user):
    return _otp_expired(user)
