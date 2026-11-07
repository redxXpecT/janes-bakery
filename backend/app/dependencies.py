import os

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()


def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is missing from .env")

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or role not in ["CUSTOMER", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return {
            "user_id": int(user_id),
            "role": role
        }

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def get_current_customer(
    identity: dict = Depends(get_current_identity)
):
    if identity["role"] != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required"
        )

    return identity


def get_current_admin(
    identity: dict = Depends(get_current_identity)
):
    if identity["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    return identity