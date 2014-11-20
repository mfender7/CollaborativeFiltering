"""
"""

from .BaseHandler import BaseHandler

class IndexHandler(BaseHandler):
    """
    """
    def get(self):
        self.render("splash.html", **self.data)

