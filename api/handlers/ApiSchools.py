from .BaseApi import BaseHandler

class ApiSchools(BaseHandler):
    """
    """
    def get(self, school_id=None, school_abbreviation=None):
        schools = self.db.schools
        values = dict(schools={school.school_id:school.school_short for school in schools}) 
        self.write(self.render_object(values))
        self.finish()
