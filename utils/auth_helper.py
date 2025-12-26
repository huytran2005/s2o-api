from db.database import SessionLocal
from models.user import User


def get_token(client, email, password="123456", role="customer"):
    # register
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )

    # set role trực tiếp (chỉ dùng cho test)
    if role != "customer":
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        user.role = role
        db.commit()
        db.close()

    # login (JSON – THEO API THẬT)
    res = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    if res.status_code != 200:
        print("LOGIN FAIL:", res.status_code, res.text)

    assert res.status_code == 200
    return res.json()["access_token"]
