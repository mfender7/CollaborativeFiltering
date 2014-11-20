"""
"""
from .BaseHandler import BaseHandler
import tornado
from . import utils


class AdminHandler(BaseHandler):
    """
    """

    def get(self):
        self.render("adminlogin.html", **self.data)

    def post(self):
        username = self.validate_item(self.get_argument("username", ""), str)
        password = self.validate_item(self.get_argument("password", ""), str)

        #print("username = "+username+" password = "+password) #dat security

        if utils.auth_admin(self.db, username, password):
            self.authorize(username)
        else:
            self.redirect("/admin")

    def authorize(self, user):
        if user:
            print("set cookie, ")
            #print(tornado.escape.json_encode(user))
            #self.set_current_user(user)
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            print("redirecting to adminpanel")
            self.redirect("/adminpanel")
        else:
            print("cleared cookie")
            self.clear_cookie("user")
            self.redirect("/admin")
            