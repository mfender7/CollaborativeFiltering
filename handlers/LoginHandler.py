"""
"""

from .utils import auth_user
import tornado.escape
from .BaseHandler import BaseHandler


class LoginHandler(BaseHandler):
    """
    """

    def get(self):
        self.render("login.html", **self.data)

    def post(self):
        username = self.validate_item(self.get_argument("username", ""), str)
        password =self.validate_item(self.get_argument("password", ""), str)

        if self.is_authorized(username, password):
            self.authorize(username)
        else:
            print("User {} failed to logged in".format(username))
            self.redirect("/login")

    def is_authorized(self, username, password):
        if auth_user(self.db, username, password):
            return True
        return False

    def authorize(self, user):
        if user:
            print("User {} logged in".format(user))
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            self.redirect("/welcome")
        else:
            print("cleared cookie")
            self.clear_cookie("user")
