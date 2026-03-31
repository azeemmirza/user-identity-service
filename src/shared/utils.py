def verify_password_policy(password: str) -> bool:
    if len(password) < 8:
        return False

    has_upper = any(character.isupper() for character in password)
    has_lower = any(character.islower() for character in password)
    has_digit = any(character.isdigit() for character in password)
    has_special = any(not character.isalnum() for character in password)

    return has_upper and has_lower and has_digit and has_special
