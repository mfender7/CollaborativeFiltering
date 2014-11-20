import scrypt
from base64 import b64encode

def auth_user(database, username, password):
    with database.session_scope() as session:
        user = database.fetch_user_by_name(session, username)
        salt = user.password_salt
        if b64encode(scrypt.hash(password, salt, database.hashlength)).decode('utf-8') == user.password_hash:
            return True
        return False

def auth_admin(database, username, password):
    with database.session_scope() as session:
        user = database.fetch_user_by_name(session, username)
        if user.admin == False:
            return False
    if auth_user(database, username, password):
        return True
    return False