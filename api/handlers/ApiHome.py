from .BaseApi import BaseHandler

class ApiHome(BaseHandler):
    """
    """
    def get(self):
        self.write(
            """
            <h1>Api Guide</h1>
            /api => this page<br>
            /api/schools => json blob of schools<br>
                {
                "schools": 
                    {
                    "<school_abbreviation>":
                        {
                        "name" : "school_name>",
                        "abbreviation" : "<school_name>",
                        "
                        }
                    }
                }

            """)