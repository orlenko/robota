import json
import os
from .env import STATE_FILE

state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)


def set(key: str, value: any):
    state[key] = value
    save()


def get(key, default=None):
    return state.get(key, default)


def save():
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
