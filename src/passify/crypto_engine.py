#crypto_engine.py

import os
from argon2.low_level import hash_secret_raw, Type
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Constants for Argon2id KDF
ARGON2_TIME_COST = 6         # Number of iterations (passes over memory)
ARGON2_MEMORY_COST = 131072  # Memory usage in KB (128 MB)
ARGON2_PARALLELISM = 2       # Number of parallel threads
ARGON2_HASH_LEN = 32         # Output key length in bytes
ARGON2_TYPE = Type.ID        # Argon2id mode (recommended)

# Vault file format constants
MAGIC_BYTES = b'SVLT'   # 4-byte file identifier
VERSION = b'\x01'       # 1-byte file format version
SALT_SIZE = 16          # Argon2 salt size
NONCE_SIZE = 12         # AES-GCM recommended nonce size

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a symmetric encryption key from a master password using Argon2id.

    Args:
        password (str): The user's master password.
        salt (bytes): A 16-byte cryptographic salt (stored with the vault file).

    Returns:
        bytes: A 32-byte symmetric key suitable for AES-256 encryption.
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    if not isinstance(salt, bytes) or len(salt) != 16:
        raise ValueError("Salt must be 16 bytes.")

    key = hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        type=ARGON2_TYPE
    )

    return key

def encrypt_vault(json_data: dict, password: str) -> bytes:
    """
    Encrypts a vault (Python dict) into a self-contained binary format using AES-GCM and Argon2id.

    Args:
        json_data (dict): The vault contents (entries, metadata, etc.).
        password (str): The master password used to derive the encryption key.

    Returns:
        bytes: A binary blob ready to be written to disk.
    """
    # Serialize the vault to JSON
    plaintext = json.dumps(json_data, separators=(',', ':')).encode('utf-8')

    # Generate encryption salt and nonce
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)

    # Derive a strong key from the master password and salt
    key = derive_key(password, salt)

    # Encrypt using AES-GCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    # Build the final vault file format
    vault_blob = MAGIC_BYTES + VERSION + salt + nonce + ciphertext
    return vault_blob

def decrypt_vault(vault_blob: bytes, password: str) -> dict:
    """
    Decrypts a vault file from bytes using AES-GCM and Argon2id.

    Args:
        vault_blob (bytes): The full contents of the encrypted vault file.
        password (str): The master password used to decrypt the vault.

    Returns:
        dict: The decrypted vault as a Python dictionary.

    Raises:
        ValueError: If the file is invalid or decryption fails.
    """
    # Check minimum length (magic + version + salt + nonce + tag)
    if len(vault_blob) < 4 + 1 + SALT_SIZE + NONCE_SIZE + 16:
        raise ValueError("Vault blob too short or corrupted.")

    # Parse header
    if vault_blob[:4] != MAGIC_BYTES:
        raise ValueError("Invalid vault file: bad magic bytes.")
    if vault_blob[4:5] != VERSION:
        raise ValueError("Unsupported vault version.")

    offset = 5
    salt = vault_blob[offset : offset + SALT_SIZE]
    offset += SALT_SIZE
    nonce = vault_blob[offset : offset + NONCE_SIZE]
    offset += NONCE_SIZE
    ciphertext = vault_blob[offset:]

    # Derive the same key
    key = derive_key(password, salt)

    # Attempt decryption
    try:
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    except Exception as e:
        raise ValueError("Decryption failed. Possibly wrong password or corrupted file.") from e

    # Decode and parse JSON
    try:
        return json.loads(plaintext.decode('utf-8'))
    except Exception as e:
        raise ValueError("Failed to parse decrypted JSON.") from e

