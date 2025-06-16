# password_gen.py

import secrets
import string

def generate_password(
    length: int = 20,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True
) -> str:
    """
    Generate a strong password with secure randomness.

    Parameters:
        length (int): Desired password length
        use_upper (bool): Include uppercase letters
        use_digits (bool): Include numbers
        use_symbols (bool): Include symbols (!@#$...)

    Returns:
        str: The generated password
    """
    alphabet = string.ascii_lowercase
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    if use_symbols:
        alphabet += "!@#$%^&*()-_=+[]{};:,.<>?"

    if not alphabet:
        raise ValueError("No characters selected for password generation.")

    return ''.join(secrets.choice(alphabet) for _ in range(length))


if __name__ == "__main__":
    # Simple CLI preview
    print("🔐 Example password:", generate_password())

