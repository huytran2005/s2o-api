from fastapi import HTTPException, status

def require_roles(user, allowed: list[str]):
    if user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
