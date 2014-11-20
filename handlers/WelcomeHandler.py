"""
"""

from tornado.web import authenticated
import tornado
from .BaseHandler import BaseHandler


class WelcomeHandler(BaseHandler):
    """
    """

    @authenticated
    def get(self):
        self.data["auth"] = True

        self.username = tornado.escape.json_decode(self.get_secure_cookie("user"))
        
        with self.db.session_scope() as session:
            self.user = self.db.fetch_user_by_name(session, self.username)
        self.data["user"] = self.user
        self.render("welcome.html", **self.data)
