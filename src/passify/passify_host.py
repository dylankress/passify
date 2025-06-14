#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from vault_manager import VaultManager

VAULT_PATH = Path.home() / ".passify" / "vault.svf"

def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        sys.exit(0)
    message_length = int.from_bytes(raw_length, byteorder="little")
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)

def send_message(response):
    encoded = json.dumps(response).encode("utf-8")
    sys.stdout.buffer.write(len(encoded).to_bytes(4, byteorder="little"))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()

def main():
    try:
        request = get_message()
        site = request.get("site")
        password = request.get("password")

        if not site or not password:
            raise ValueError("Missing 'site' or 'password' in request.")

        vm = VaultManager(VAULT_PATH)
        vm.load_from_file(password)
        entry = vm.get_entry(site)

        if entry:
            send_message({"success": True, "entry": entry})
        else:
            send_message({"success": False, "error": "Site not found"})
    except Exception as e:
        send_message({"success": False, "error": str(e)})

if __name__ == "__main__":
    main()

