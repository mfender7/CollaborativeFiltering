"""
Database for storing course information
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String


class OpinionDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class):
        """
        """

        class OpinionTable(base_class):
            """
            """
            __tablename__ = "opinions"
            # creation info
            user_id = Column(sqlalchemy.Integer, primary_key=True)
            item_id = Column(sqlalchemy.Integer, primary_key=True)
            rating = Column(sqlalchemy.Float, nullable=True)

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Opinion for item {} by user {}({})>".format(self.item_id, self.user_id, self.rating)

        this.class_ = CourseTable

    def create(this):
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = OpinionDatabase(sqlalchemy.ext.declarative.declarative_base()).create()
