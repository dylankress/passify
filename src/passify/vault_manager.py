#vault_manager.py

from crypto_engine import decrypt_vault
from crypto_engine import encrypt_vault
import os
from pathlib import Path
import csv
from typing import Union

DEFAULT_VAULT_PATH = Path.home() / ".passify" / "vault.svf"

class VaultManager:
    def __init__(self, vault_path: Path = DEFAULT_VAULT_PATH):
        self.vault_path = vault_path
        self.vault = {
            "version": 1,
            "entries": []
        }
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)

    def load_from_file(self, password: str, filepath: Union[str, Path] = None) -> None:
        filepath = Path(filepath) if filepath else self.vault_path
        with open(filepath, "rb") as f:
            encrypted_data = f.read()
        self.vault = decrypt_vault(encrypted_data, password)

    def save_to_file(self, password: str, filepath: str = None) -> None:
        filepath = Path(filepath) if filepath else self.vault_path
        encrypted_data = encrypt_vault(self.vault, password)
        with open(filepath, "wb") as f:
            f.write(encrypted_data)

    def add_entry(self, name: str, url: str, username: str, password: str) -> None:
        """
        Adds a new Chrome-compatible entry to the vault.
        """
        new_entry = {
            "name": name,
            "url": url,
            "username": username,
            "password": password
        }
        self.vault["entries"].append(new_entry)

    def get_entry(self, name: str) -> dict | None:
        """
        Retrieves the first entry that matches the given name (domain label).
        """
        for entry in self.vault["entries"]:
            if entry["name"].lower() == name.lower():
                return entry
        return None

    def update_entry(self, name: str, username: str = None, password: str = None, url: str = None) -> bool:
        """
        Updates fields of an existing entry matching `name`.
        """
        for entry in self.vault["entries"]:
            if entry["name"].lower() == name.lower():
                if username is not None:
                    entry["username"] = username
                if password is not None:
                    entry["password"] = password
                if url is not None:
                    entry["url"] = url
                return True
        return False

    def delete_entry(self, name: str) -> bool:
        for i, entry in enumerate(self.vault["entries"]):
            if entry["name"].lower() == name.lower():
                del self.vault["entries"][i]
                return True
        return False

    def list_entries(self) -> list[str]:
        """
        Returns a list of saved site names (Chrome's `name` field).
        """
        return [entry["name"] for entry in self.vault["entries"]]

    def import_from_chrome_csv(self, csv_path: str) -> int:
        import csv
        count = 0
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("name") and row.get("url") and row.get("username") and row.get("password"):
                    self.add_entry(
                        name=row["name"],
                        url=row["url"],
                        username=row["username"],
                        password=row["password"]
                    )
                    count += 1
        return count

