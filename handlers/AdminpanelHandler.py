"""
"""
from tornado.web import authenticated
from .BaseHandler import BaseHandler


class AdminpanelHandler(BaseHandler):
    """
    """
    @authenticated
    def get(self):
        self.user = self.get_user_obj()
        if self.user.admin:
            self.data["auth"] = True
            self.data["schools"] = self.db.schools

            #this I would consider the blackest of magicks
            with self.db.session_scope() as session:
                for school in self.data["schools"]:
                    session.add(school)
                    school.numcourses = len(school.courses)
                    school.numstudents = len(school.students)
            self.data["users"] = self.db.users
            self.data["user"] = self.user

            self.render("adminpanel.html", **self.data)
        else:
            self.redirect("/welcome")


    @authenticated
    def post(self):
        self.user = self.get_user_obj()
        
        school_name = self.validate_item(self.get_argument("school_name", ""), str)
        school_short = self.validate_item(self.get_argument("school_short", ""), str)
        if all([school_name, school_short]):
            with self.db.session_scope() as session:
                self.db.add_school(session, school_name, school_short)

        with self.db.session_scope() as session:
            self.data["auth"] = True
            self.data["schools"] = self.db.schools
            self.data["users"] = self.db.users
            self.data["user"] = self.user

            for school in self.data["schools"]:
                session.add(school)
                school.numcourses = len(school.courses)
                school.numstudents = len(school.students)

            self.render("adminpanel.html", **self.data)
