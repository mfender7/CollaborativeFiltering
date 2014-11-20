from tornado.web import authenticated
from .BaseHandler import BaseHandler
from .utils import auth_user

class SettingsHandler(BaseHandler):
    """
    """
        
    @authenticated
    def get(self):
        self.data["auth"] = True
        self.data["user"] = self.get_user_obj()

        self.render("settings.html", **self.data)

    @authenticated
    def post(self):
        self.data["auth"] = True
        self.data["user"] = self.get_user_obj()

        if self.validate_item(self.get_argument("password", default=None), str) == "true":
            if auth_user(self.db, self.data["user"].user_name, self.validate_item(self.get_argument("current_pw"), str)):
                with self.db.session_scope() as session:
                    self.db.update_password(session, self.data["user"].user_name, self.validate_item(self.get_argument("new_password", default=None), str))
        else:
            #get args
            first_name = self.get_argument("fname", default=None, strip=True)
            last_name = self.get_argument("lname", default=None, strip=True)
            email = self.get_argument("email", default=None, strip=True)
            age = self.get_argument("age", default=0, strip=True)
            grad = self.get_argument("grad", default=0, strip=True)

            values = {
                "first":(first_name, str), 
                "last":(last_name, str), 
                "email_address":(email,str), 
                "age":(age,int),
                "graduation":(grad,int)}
            values = self.validate_form(**values)
            with self.db.session_scope() as session:
                if {values[key] for key in values} != {None}:
                    self.db.update_user(session, self.username, **values)


        self.render("settings.html", **self.data)



    def get_template_namespace(self):
        #This is a bit of a hack, but it works
        namespace = BaseHandler.get_template_namespace(self)

        def fetch_school(school):
            with self.db.session_scope() as session:
                 return self.db.fetch_school_by_id(session, school)

        namespace = dict(fetch_school=fetch_school,**namespace)
        namespace.update(self.ui)
        return namespace
