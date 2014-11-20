"""
"""
from .BaseHandler import BaseHandler


class RegisterHandler(BaseHandler):
    """
    """

    def get(self):
        self.render("register.html", **self.data)

    def post(self):
        username = self.validate_item(self.get_argument("username", ""), str)
        email = self.validate_item(self.get_argument("email", ""), str)
        school = self.validate_item(self.get_argument("school", ""), str)
        password = self.validate_item(self.get_argument("password", ""), str)
        password2 = self.validate_item(self.get_argument("password2", ""), str)

        if username != "" and email != "" and password == password2 and school != "" and len(password) < 256:
            with self.db.session_scope() as session:
                self.db.add_user(session, username, email, password, school)
            self.redirect("/login")
        else:
            self.redirect("/register")
