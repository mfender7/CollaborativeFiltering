"""
Database for storing ratings
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String


class SimilarityDatabase(object):
    """
    Factory for creating ratings databases
    """

    def __init__(this, base_class):
        """
        Creates a class to store user data, based on some provided information
        """
        class SimilarityTable(base_class):
            """
            """
            __tablename__ = "similarities"
            # creation info
            usera_id = Column(sqlalchemy.Integer, primary_key=True)
            userb_id = Column(sqlalchemy.Integer, primary_key=True)
            a = Column(sqlalchemy.Float, nullable=False)
            b = Column(sqlalchemy.Float, nullable=False)

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Similarity {} of user {} with user' {}>".format(self.a/self.b, self.usera_id, self.userb_id)

        this.class_ = RatingTable

    def create(this):
        """
        Returns the SimilarityTable class
        """
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = SimilarityDatabase(sqlalchemy.ext.declarative.declarative_base(), "test").create()
