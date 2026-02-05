
# tests password's policy
def verify_password_policy(password: str) -> bool:
    if len(password) < 8:
        return False

    return True