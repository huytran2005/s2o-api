from fastapi import Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from utils.jwt import verify_token

from db.database import get_db
from models.user import User
from utils.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from models.guest_session import GuestSession


def get_guest_session(
    guest_session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not guest_session:
        raise HTTPException(status_code=401, detail="Missing session")

    session = (
        db.query(GuestSession)
        .filter(
            GuestSession.session_token == guest_session,
            GuestSession.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    return session


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

# utils/dependencies.py
def get_current_user_optional(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        return None

    token = auth.replace("Bearer ", "")
    return verify_token(token)
# utils/dependencies_mobile.py

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from models.guest_session import GuestSession


def get_guest_session_mobile(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    token = authorization.replace("Bearer ", "")

    session = (
        db.query(GuestSession)
        .filter(
            GuestSession.session_token == token,
            GuestSession.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=401, detail="Session expired")

    return session
