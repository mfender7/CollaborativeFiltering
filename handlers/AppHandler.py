"""
"""

from tornado.web import authenticated
from .BaseHandler import BaseHandler

class AppHandler(BaseHandler):
    """
    """
        
    def get_current_user(self):
        return self.get_secure_cookie("user")

    @authenticated
    def get(self):
        self.data["auth"] = True
        self.render("app_main.html")
