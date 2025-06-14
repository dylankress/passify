from crypto_engine import derive_key, encrypt_vault
import os
import json
from crypto_engine import decrypt_vault

# Test derive_key() on its own
password = "hunter2"
salt = os.urandom(16)
key = derive_key(password, salt)

print(f"Derived key (hex): {key.hex()}")
print(f"Key length: {len(key)} bytes")  # Should be 32

# Build a test vault
vault = {
    "version": 1,
    "entries": [
        {
            "site": "test.com",
            "username": "user",
            "password": "hunter2"
        }
    ]
}

# Encrypt and save vault
password = "strongmasterpassword"
blob = encrypt_vault(vault, password)

with open("vault.svf", "wb") as f:
    f.write(blob)

print("Vault saved successfully.")

with open("vault.svf", "rb") as f:
    blob = f.read()

password = "strongmasterpassword"
vault = decrypt_vault(blob, password)

print("Decrypted vault:")
print(vault)
