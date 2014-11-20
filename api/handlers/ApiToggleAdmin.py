from .BaseApi import BaseHandler
from tornado.web import authenticated


class ApiToggleAdmin(BaseHandler):
    """
    """
    @authenticated
    def get(self, user_id):
        self.get_user_obj()
        if self.user.admin is True:
            with self.db.session_scope() as session:
                other = self.db.fetch_user_by_id(session, user_id)
                if self.user.user_id is not other.user_id:
                    other.admin = not other.admin
            self.redirect("/adminpanel")
        else:
            self.redirect("/welcome") 