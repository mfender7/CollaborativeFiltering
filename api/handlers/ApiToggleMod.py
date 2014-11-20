from .BaseApi import BaseHandler
from tornado.web import authenticated


class ApiToggleMod(BaseHandler):
    """
    """
    @authenticated
    def get(self, user_id):
        self.get_user_obj()
        if self.user.admin is True or self.user.admin is True:
            with self.db.session_scope() as session:
                other = self.db.fetch_user_by_id(session, user_id)
                other.moderator = not other.moderator
            self.redirect("/adminpanel")
        else:
            self.redirect("/welcome") 