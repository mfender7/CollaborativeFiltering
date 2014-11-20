"""
Database for storing course information
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String


class CourseDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class):
        """
        """

        class CourseTable(base_class):
            """
            """
            __tablename__ = "courses"
            # creation info
            course_id = Column(sqlalchemy.Integer, primary_key=True)
            school_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("schools.school_id"))
            course_name = Column(String(64), nullable=True)
            identifier = Column(String(16), nullable=False)
            # optional info
            professor = Column(String(64), nullable=True)
            year = Column(sqlalchemy.Integer, nullable=True)
            semester = Column(sqlalchemy.String(), nullable=True)

            sqlalchemy.UniqueConstraint("identifier", "school_id", "professor", "year", "semester")

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Course {} ({})>".format(self.identifier, self.course_name)

        this.class_ = CourseTable

    def create(this):
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = CourseDatabase(sqlalchemy.ext.declarative.declarative_base()).create()
