from tornado.websocket import WebSocketHandler

class BaseSocket(WebSocketHandler):
    """
    a base class for websockets
    """

    def initialize(self, db):
        self.db = db

    def is_authenticated(self, user_name, password_hash):
        with self.db.session_scope() as session:
            user = self.db.fetch_user_by_name(session, user_name)
            if user.apikey == password_hash:
                return True
        return False

    def get_user_obj(self, username):
        self.username = username
        with self.db.session_scope() as session:
            user = self.db.fetch_user_by_name(session, self.username)
        return user