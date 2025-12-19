# services/auth_service.py
def authenticate_user(user, password):
    from utils.security import verify_password
    if not user:
        return False
    return verify_password(password, user.password_hash)
