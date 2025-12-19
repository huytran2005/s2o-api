import bcrypt

def hash_password(password: str) -> str:
    # DÙNG rounds thấp cho môi trường DEV/TEST cho nhanh
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=4),  # mặc định ~12, rất nặng
    ).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )