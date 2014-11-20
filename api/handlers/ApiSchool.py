from .BaseApi import BaseHandler
from databases.database import ItemDoesNotExistError

class ApiSchool(BaseHandler):
    """
    """
    def get(self, school_value):
        try:
            school_id = int(school_value)
            school_abbr = None
        except ValueError:
            school_abbr = " ".join(school_value.split("_"))
            school_id = None

        with self.db.session_scope() as session:
            try:
                if school_id:
                    school = self.db.fetch_school_by_id(session, school_id)
                else:
                    school = self.db.fetch_school_by_name(session, school_abbr)
            
                if school is None:
                    self.write(self.render_object(dict(Error="No school found")))
                else:
                    values = {}
                    values["school_name"] = school.school_name
                    values["school_short"] = school.school_short
                    values["school_id"] = school.school_id
                    values["courses"] = [str(course.identifier) for course in school.courses]
                    values["studends"] = [str(student.user_name) for student in school.students]

                    self.write(self.render_object(values))
                    self.finish()

            except ItemDoesNotExistError:
                self.write(self.render_object(dict(Error="No school found")))
