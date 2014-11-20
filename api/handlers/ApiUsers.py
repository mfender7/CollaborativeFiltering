from .BaseApi import BaseHandler

class ApiUsers(BaseHandler):
    """
    """
    def get(self, school_id=None, school_abbreviation=None):
        users = self.db.users
        values = dict(schools={user.user_id:user.user_name for user in users}) 
        self.write(self.render_object(values))
        self.finish()
