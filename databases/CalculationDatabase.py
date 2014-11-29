"""
Database for storing users
"""

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
from sqlalchemy import Column, String


class CalculationDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class):
        """
        This instantiates an object with the given settings (namely hashlength)
            and returns an instance of the new class when create is called

        This also allows additional class specific methods to be added to the
            class, for example if hashing were to be handled within the user
            class instead of in the database overall class it could be done that
            way.

        groups are the group that a user belongs to, currently only one is possible.
        """

        class CalculationTable(base_class):
            """
            """
            __tablename__ = "calculations"
            # signup info
            user_id = Column(sqlalchemy.Integer, primary_key=True)
            item_id = Column(sqlalchemy.Integer, primary_key=True)
            rating = Column(sqlalchemy.Float, nullable=False)

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Calculated rating of user {} for item {} ({})>".format(self.user_id, self.item_id, self.rating)

        this.class_ = CalculationTable

    def create(this):
        """
        returns an instance of the new class, should basically always be run
        unless something strange is happening
        """
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = CalculationDatabase(sqlalchemy.ext.declarative.declarative_base(), 64, "test", "test").create()
