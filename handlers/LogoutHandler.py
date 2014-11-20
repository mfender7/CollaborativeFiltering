"""
"""

from .BaseHandler import BaseHandler

class LogoutHandler(BaseHandler):
    """
    """
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")
