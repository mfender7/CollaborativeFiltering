from .BaseHandler import BaseHandler
from collections import defaultdict
from tornado.web import authenticated

class AdminSchoolHandler(BaseHandler):

    @authenticated
    def get(self, school_id):
        self.data["user"] = self.get_user_obj()
        if self.user.admin:
            self.data["auth"] = True
            with self.db.session_scope() as session:
                self.data["users"] = self.db.fetch_school_by_id(session, school_id).students
                self.data["courses"] = self.db.fetch_school_by_id(session, school_id).courses
            self.render("modpanel.html", **self.data)
        else:
            self.redirect("/welcome")


    @authenticated
    def post(self):
        self.data["user"] = self.get_user_obj()
        if self.user.admin:
            self.data["auth"] = True
            course_name = self.validate_item(self.get_argument("course_name"), str)
            course_abbreviation = self.validate_item(self.get_argument("course_identifier"), str)
            professor = self.validate_item(self.get_argument("professor", None), str)
            year = self.validate_item(self.get_argument("year", None), int)
            semesterdict = defaultdict(None)
            semester = self.validate_item(self.get_argument("semester", None), str)

            # Crappy implementation of the semester Enum
            semesters = {"Fall":"Fall","Spring":"Spr","Summer":"Sum","Winter":"Win"}
            for k in semesters:
                semesterdict[k] = semesters[k]
            semester = semesterdict[semester]

            with self.db.session_scope() as session:
                if all([course_name is not None, course_abbreviation is not None]):
                    self.db.add_course(session, self.db.fetch_school_by_id(session, self.user.school_id).school_short, course_name, course_abbreviation, professor=professor, year=year, semester=semester)
                self.data["users"] = self.db.fetch_school_by_id(session, self.user.school_id).students
                self.data["courses"] = self.db.fetch_school_by_id(session, self.user.school_id).courses
            self.render("modpanel.html", **self.data)
        else:
            self.redirect("/welcome")