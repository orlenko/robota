import json
import os
from .env import STATE_FILE

state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)


def set(key, value):
    state[key] = value
    save()


def get(key):
    return state.get(key)


def save():
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
