from api.models import User

def format_user(user: User):
    return {
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "middlename": user.middlename,
        "avatar": user.avatar,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }