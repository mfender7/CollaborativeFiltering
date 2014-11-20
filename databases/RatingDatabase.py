"""
Database for storing ratings
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String


class RatingDatabase(object):
    """
    Factory for creating ratings databases
    """

    def __init__(this, base_class, course_):
        """
        Creates a class to store user data, based on some provided information
        """
        class RatingTable(base_class):
            """
            """
            __tablename__ = "ratings"
            # creation info
            user_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), primary_key=True)
            course_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("courses.course_id"), primary_key=True)
            # attributes
            rating = Column(sqlalchemy.Integer, nullable=True)  # how much one liked the course wholistically
            grade = Column(sqlalchemy.Integer, nullable=True)  # how well the student did
            difficulty = Column(sqlalchemy.Integer, nullable=True)  # how difficult they felt the course was
            year = Column(sqlalchemy.Integer, nullable=True)  # year you took it
            professor = Column(String(64), nullable=True)  # prof that taught it
            semester = Column(String(4), nullable=True)  # semester, spr, sum, fall, wint
            # relations
            course = sqlalchemy.orm.relationship(course_, backref="ratings")

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Rating of {} by user {} for course {}>".format(self.rating, self.course_id, self.user_id)

        this.class_ = RatingTable

    def create(this):
        """
        Returns the UserTable class
        """
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = RatingDatabase(sqlalchemy.ext.declarative.declarative_base(), "test").create()
