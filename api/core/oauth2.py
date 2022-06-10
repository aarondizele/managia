
from typing import Optional
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import encode, decode, exceptions
from datetime import datetime, timedelta
from os import getenv

from api.core.schemas import UserOAuth
from api.models import User
from sqlalchemy.orm import Session
from api import database


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def expire_date(days: int):
    date = datetime.now()
    new_date = date + timedelta(days)
    return new_date


def write_token(data: dict):
    token = encode(
        payload={
            **data, "exp": expire_date(int(getenv("JWT_EXPIRATION_TIME")))},
        key=getenv("JWT_SECRET"),
        algorithm="HS256"
    )
    return token


def validate_token(token, output=False):
    try:
        if output:
            return decode(token, key=getenv("JWT_SECRET"), algorithms=["HS256"])
        decode(token, key=getenv("JWT_SECRET"), algorithms=["HS256"])
    except exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = database.session()):
    payload = validate_token(token, output=True)
    email: str = payload.get("sub")

    # Find user from DB
    user: Optional[User] = db.query(User).filter(User.email == email).first()

    # If user not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


    userOAuth = UserOAuth(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        roles=user.roles
    )

    return userOAuth


async def get_current_active_user(current_user: UserOAuth = Depends(get_current_user)):
    if current_user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
