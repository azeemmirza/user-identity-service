'''
doc string
'''
def verify_password_policy(password: str) -> bool:
    '''
    doc string
    '''
    if len(password) < 8:
        return False

    return True
