"""
The base class from which most (all? other handlers will inherit)
"""
from tornado.web import RequestHandler
import tornado


class BaseHandler(RequestHandler):
    """
    """
    def get_current_user(self):
        """
        An override to the builtin @authenticate, can be rewritten to be better
            if eventually necessary
        """
        return self.get_secure_cookie("user")


    def initialize(self, db):
        """
        Gives the handler some base information that it can then change
        """
        if self.get_secure_cookie("user"):
            self.username = tornado.escape.json_decode(self.get_secure_cookie("user"))
        self.db = db
        self.data = {"auth":False, "user":None, "socketbase":"ws://boiling-crag-4069.herokuapp.com/"}

    def get_user_obj(self):
        self.username = tornado.escape.json_decode(self.get_secure_cookie("user"))
        with self.db.session_scope() as session:
            self.user = self.db.fetch_user_by_name(session, self.username)
        return self.user

    def validate_form(self, **kwargs):
        """
        kwargs should be a dict<formname : tuple(value, type(value))>
        """
        result = {}
        for form in kwargs:
            try:
                result[form] = kwargs[form][1](kwargs[form][0])
                if result[form] == "":
                    result[form] = None
            except:
                result[form] = None
        return result

    def validate_item(self, form_item, type_):
        """
        Validates the input from a form, given a string and the type of the item
            this returns the item converted to that type or None, if it can't be
            converted or the form is blank
        """
        if form_item == "":
            return None
        else:
            try:
                return type_(form_item)
            except TypeError:
                return None

    #do not override get_template_namespace()
    