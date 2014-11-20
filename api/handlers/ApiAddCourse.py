from .BaseSocket import BaseSocket
from tornado.escape import json_decode, json_encode

class ApiAddCourse(BaseSocket):
    """
    """
    def open(self):
        pass

    def on_message(self, message):
        data = json_decode(message)
        self.user = self.get_user_obj(data["username"])
        if self.is_authenticated(data["username"], data["apikey"]):
            with self.db.session_scope() as session:
                course = self.db.fetch_course_by_id(session, data["course"])
                self.db.add_rating(session, data["username"], course.identifier, semester=course.semester, professor=course.professor, year=course.year, rating=None, difficulty=None, grade=None)
            self.write_message(json_encode({"stat":"added"}))
        else:
            self.write_message(json_encode({"stat":"failed"}))
