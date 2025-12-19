#!/usr/bin/env python3

import argparse
import subprocess
import re
import yaml
import os
import json
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ------------------------
# CLI Args
# ------------------------

parser = argparse.ArgumentParser(description="Monitor NFS server status via kernel logs.")
parser.add_argument("--config", required=True, help="Path to YAML config file")
parser.add_argument("--dry-run", action="store_true", help="Do not send Slack messages or write state/logs")
args = parser.parse_args()

# ------------------------
# Load config
# ------------------------

with open(args.config) as f:
    config = yaml.safe_load(f)

SLACK_TOKEN = config["slack_token"]
SLACK_CHANNEL = config["slack_channel"]
SERVERS = config["servers"]  # dict: { identifier: name }
STATE_DIR = config["state_dir"]
LOG_FILE = config["log_file"]
SENDER = config["sender"]
DEBOUNCE = timedelta(minutes=config.get("debounce_minutes", 10))

slack_client = WebClient(token=SLACK_TOKEN)

os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ------------------------
# Helpers
# ------------------------

def send_slack(message):
    if args.dry_run:
        print(f"[dry-run] Slack to {SLACK_CHANNEL}: {message}")
        return
    try:
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    except SlackApiError as e:
        print(f"[error] Slack API error: {e.response['error']}")

def log_event(text):
    line = f"[{datetime.now().isoformat()}] {text}"
    if args.dry_run:
        print(f"[dry-run] Log: {line}")
        return
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_state_file(identifier):
    safe = identifier.replace("/", "_")
    return os.path.join(STATE_DIR, f"{safe}.state")

def read_last_status(identifier):
    path = get_state_file(identifier)
    if not os.path.exists(path):
        return None, None
    with open(path) as f:
        data = json.load(f)
        return data.get("status"), datetime.fromisoformat(data.get("changed"))

def write_status(identifier, status):
    if args.dry_run:
        print(f"[dry-run] Would write status '{status}' to {get_state_file(identifier)}")
        return
    with open(get_state_file(identifier), "w") as f:
        json.dump({
            "status": status,
            "changed": datetime.now().isoformat()
        }, f)

def parse_kern_messages():
    """Returns dict of {identifier: status} seen in recent kernel messages."""
    try:
        output = subprocess.check_output(["sudo", "journalctl", "-k", "--since", "10 minutes ago"], text=True)
    except subprocess.CalledProcessError:
        return {}

    results = {}
    for line in output.splitlines():
        match = re.search(r'nfs: server (\S+) (not responding|OK)', line)
        if match:
            identifier, state = match.groups()
            if identifier in SERVERS:
                results[identifier] = state
    return results

# ------------------------
# Main logic
# ------------------------

current_status = parse_kern_messages()

for identifier in SERVERS:
    name = SERVERS[identifier]
    new = current_status.get(identifier)
    if not new:
        continue  # no recent update

    old, last_changed = read_last_status(identifier)

    if new != old:
        recently_changed = last_changed and (datetime.now() - last_changed < DEBOUNCE)

        if not recently_changed:
            emoji = ":large_green_circle:" if new == "OK" else ":red_circle:"
            send_slack(f"{emoji} NFS monitor for *{SENDER}*: *{name} ({identifier})* status: *{new}*")
            log_event(f"{identifier} ({name}) → {new}")
        else:
            if args.dry_run:
                print(f"[dry-run] Suppressed Slack (debounced): {identifier} status: {new}")

        write_status(identifier, new)

