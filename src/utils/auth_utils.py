import hashlib
import os
from werkzeug.security import check_password_hash, generate_password_hash

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return generate_password_hash(password)

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    return check_password_hash(stored_password, provided_password)

def legacy_hash_password(password: str) -> str:
    """Hash a password for storing using legacy method."""
    salt = os.urandom(32)  # 32 bytes = 256 bits
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + key.hex()

def legacy_verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user using legacy method."""
    salt_hex, key_hex = stored_password.split(':')
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return key.hex() == key_hex 