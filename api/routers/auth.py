from uuid import uuid1
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from api.core.oauth2 import UserOAuth, write_token, validate_token, get_current_active_user
from api.models import ResetCode, User
from api.core.hashing import Hash
from api.core.schemas import ChangePasswordSchema, LoginSchema, RegisterUserAdminSchema, ResetPasswordSchema
from api.formating import format_user
from starlette.requests import Request as request
from api.exceptions import UserNotFoundException
from sqlalchemy.orm import Session
from api import database
from api.mailing import send_forgot_password_mail


router = APIRouter(
    tags=["Authenticate"]
)


@router.post("/auth/login")
def login(schema: LoginSchema, db: Session = database.session()):
    user: Optional[User] = db.query(User).filter(
        User.email == schema.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not Hash.verify(schema.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token: str = write_token({"sub": user.email})

    return {"access_token": token}


@router.get("/user/me")
def get_user_profile(
    current_user: UserOAuth = Depends(get_current_active_user),
    db: Session = database.session()
):

    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise UserNotFoundException()

    return format_user(user)


@router.post("/auth/verify/token")
def verify_token(Authorization: str = Header(None)):
    token = Authorization.split(" ")[1]
    return validate_token(token, output=True)


@router.post('/auth/register/super-admin')
async def create_user(schema: RegisterUserAdminSchema, db: Session = database.session()):

    user_exists = db.query(User).filter(User.email == schema.email).first()

    if not user_exists:
        new_user = User(
            email=schema.email,
            hashed_password=Hash.bcrypt(schema.password),
            firstname=schema.firstname,
            lastname=schema.lastname,
            middlename=schema.middlename,
            roles=['super_admin'],
            created_at=datetime.now(),
        )

        db.add(new_user)
        db.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED)

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already registered",
    )


@router.post('/user/forgot-password')
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    db: Session = database.session()
):

    user_exists = db.query(User).filter(User.email == email).first()

    if not user_exists:
        raise UserNotFoundException()

    # Create reset code and save it to DB
    reset_code = str(uuid1())

    storedResetCode = ResetCode(
        email=email,
        reset_code=reset_code,
        created_at=datetime.now(),
    )

    db.add(storedResetCode)
    db.commit()

    # Send emai
    background_tasks(send_email, email, reset_code)

    return JSONResponse(status_code=status.HTTP_200_OK)


@router.put('/user/reset-password')
async def reset_password(schema: ResetPasswordSchema, db: Session = database.session()):

    # Check if passwords matches
    if (schema.new_password is not schema.confirm_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Password not match'
        )

    # Reset code query
    reset_code_query = (db.query(ResetCode)
                        .filter(ResetCode.reset_code == schema.reset_password_token))

    # Rest code object
    reset_code: Optional[ResetCode] = reset_code_query.first()

    # Check if reset code doesn't exist
    if not reset_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Reset password token expired'
        )

    # check if expiration date is expired
    if datetime.now() > reset_code.expires_in:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Reset password token expired'
        )

    # User query
    user_query = (db.query(User)
                    .filter(User.email == reset_code.email))
    # User object
    user: Optional[User] = user_query.first()

    if not user:
        raise UserNotFoundException()

    user_query.update({
        "hashed_password": Hash.bcrypt(schema.new_password)
    }, synchronize_session=False)

    reset_code_query.delete(synchronize_session=False)

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content='Password has been reset successfully.'
    )


@router.delete('/user/profile')
async def deactivate_account(current_user: UserOAuth = Depends(get_current_active_user), db: Session = database.session()):
    # User query
    user_query = (db.query(User)
                    .filter(User.id == current_user.id))
    # User object
    user: Optional[User] = user_query.first()

    if not user:
        raise UserNotFoundException()

    user_query.update({"is_active": False}, synchronize_session=False)

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content='Your account has been deactivated successfully.'
    )


@router.put('/user/change-password')
async def change_password(schema: ChangePasswordSchema, current_user: UserOAuth = Depends(get_current_active_user), db: Session = database.session()):
    if (schema.new_password != schema.confirm_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Password not match'
        )

    # User query
    user_query = (db.query(User)
                    .filter(User.id == current_user.id))
    # User object
    user: Optional[User] = user_query.first()

    if not user:
        raise UserNotFoundException()

    if not Hash.verify(schema.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    user_query.update({
        "hashed_password": Hash.bcrypt(schema.new_password)
    }, synchronize_session=False)

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content='Your password has been changed successfully.'
    )


async def send_email(email: EmailStr, reset_code: str):
    # Mailjet Email API
    message = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reset password</title>
        </head>
        <body>
            <div style="width: 100%;font-family: monospace;">
                <h1>Hello, {0:}</h1>
                <p>Someone has requested a link to reset your password. If you requested this, you can change your password through the following link <br>
                <a href="{1:}/user/reset-password?reset_password_token={2:}" style="box-sizing: border-box;text-decoration: underline;">Reset password</a>
                </p>
                <p>If you didn't request this, you can ignore this email.</p>
                <p>Your password won't chamge until you access the link above and create a new</p>
            </div>
        </body>
        </html>
    """.format(email, request.base_url, reset_code)

    await send_forgot_password_mail(email, message)
