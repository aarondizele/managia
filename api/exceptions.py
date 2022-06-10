from http.client import HTTPException


def UserNotFoundException():
    HTTPException(
        status_code=404,
        detail='User not found'
    )
