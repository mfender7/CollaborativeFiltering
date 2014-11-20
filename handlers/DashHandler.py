"""
"""

from tornado.web import authenticated
from .BaseHandler import BaseHandler

class DashHandler(BaseHandler):
    """
    """
    
    @authenticated
    def get(self):
        self.data["user"] = self.get_user_obj()
        self.data["auth"] = True
        with self.db.session_scope() as session:
            self.data["school_courses"] = self.db.fetch_school_by_id(session, self.user.school_id).courses
            session.add(self.user)
            self.data["your_courses"] = self.user.courses
            self.data["your_ratings"] = {course.course_id : self.db.fetch_rating_by_id(session, self.data["user"].user_id, course.course_id) for course in self.data["your_courses"]}
        self.render("dash.html", **self.data)

    @authenticated
    def post(self):
        self.data["user"] = self.get_user_obj()
        self.data["auth"] = True
        if self.get_argument("submit", False):
            course_id = self.validate_item(self.get_argument("submit"), int)
            with self.db.session_scope() as session:
                course = self.db.fetch_course_by_id(session, course_id)
                rating = self.validate_item(self.get_argument("rating-"+str(course.course_id)), int)
                difficulty = self.validate_item(self.get_argument("difficulty-"+str(course.course_id)), int)
                grade = self.validate_item(self.get_argument("grade-"+str(course.course_id)), int)
                if any([grade, difficulty, rating]):
                    self.db.update_rating(session, self.data["user"].user_name, course.identifier, oldyear=course.year, oldprof=course.professor, oldsem=course.semester, grade=grade, rating=rating, difficulty=difficulty)
        else:
            deleted_id = self.validate_item(self.get_argument("delete"), int)
            with self.db.session_scope() as session:
                course = self.db.fetch_course_by_id(session, deleted_id)
                self.db.remove_rating(session, self.data["user"].user_name, course.identifier, semester=course.semester, year=course.year, professor=course.professor)
        with self.db.session_scope() as session:
            self.data["school_courses"] = self.db.fetch_school_by_id(session, self.user.school_id).courses
            session.add(self.user)
            self.data["your_courses"] = self.user.courses
            self.data["your_ratings"] = {course.course_id : self.db.fetch_rating_by_id(session, self.data["user"].user_id, course.course_id) for course in self.data["your_courses"]}
        self.render("dash.html", **self.data)
