from .BaseApi import BaseHandler
from databases.database import ItemDoesNotExistError

class ApiUser(BaseHandler):
    """
    """
    def get(self, user_value):
        try:
            user_id = int(user_value)
            user_name = None
        except ValueError:
            user_name = " ".join(user_value.split("_"))
            user_id = None

        with self.db.session_scope() as session:
            try:
                if user_id:
                    user = self.db.fetch_user_by_id(session, user_id)
                else:
                    user = self.db.fetch_user_by_name(session, user_name)
            
                if user is None:
                    self.write(self.render_object(dict(Error="No school found")))
                else:
                    values = {}
                    values["school_id"] = user.school_id
                    values["user_name"] = user.user_name
                    values["first_name"] = user.first_name
                    values["last_name"] = user.last_name
                    values["last_name"] = user.last_name
                    values["age"] = user.age
                    values["graduation"] = user.graduation
                    values["admin"] = user.admin
                    values["moderator"] = user.moderator
                    values["courses"] = [str(course.course_name) for course in user.courses]

                    self.write(self.render_object(values))
                    self.finish()

            except ItemDoesNotExistError:
                self.write(self.render_object(dict(Error="No school found")))
