"""
Database for storing users
"""

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
from sqlalchemy import Column, String


class SchoolDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class, course_, user_):
        """
        This instantiates an object with the given settings (namely hashlength)
            and returns an instance of the new class when create is called

        This also allows additional class specific methods to be added to the
            class, for example if hashing were to be handled within the user
            class instead of in the database overall class it could be done that
            way.

        groups are the group that a user belongs to, currently only one is possible.
        """

        class SchoolTable(base_class):
            """
            """
            __tablename__ = "schools"
            # creation info
            school_id = Column(sqlalchemy.Integer, primary_key=True)
            school_name = Column(String(64), nullable=False)
            school_short = Column(String(32), nullable=False)
            # relations
            courses = sqlalchemy.orm.relationship(course_, backref="school")
            students = sqlalchemy.orm.relationship(user_, backref="school")

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<School {} ({})>".format(self.school_name, self.school_short or "")

        this.class_ = SchoolTable

    def create(this):
        """
        returns an instance of the new class, should basically always be run
        unless something strange is happening
        """
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = SchoolDatabase(sqlalchemy.ext.declarative.declarative_base(), 64, "test", "test").create()
