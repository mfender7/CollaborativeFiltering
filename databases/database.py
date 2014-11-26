"""
drop in (hopefully) replacement for the database class
developed by Joshua Morton

Now with more DRY!

"""

from enum import Enum
from contextlib import contextmanager
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import _or
from . import CalculationDatabase
from . import OpinionDatabase
from . import SimilarityDatabase
import hashlib
import os
from  base64 import b64encode


class Database(object):
    """
    An abstraction of an sql database for managing user and class information.

    instance data that might be relevant:
        hashlength -- the length of password hashes
        course -- the table of courses
        rating -- the table of ratings (many to many link between course and user)
        user -- the table of users
        school -- the table of school (one to many with user and course)
        sessionmaker -- a factory for sessions, can be used by external tools to make specialized database queries
    """

    def __init__(self, name="ClassRank.db", folder="data"):
        """
        initializes the database, creates tables and files as necessary

        Keyword Arguments:
            name -- the name of the database file, created as necessary
            table -- the table, a holdover from previous versions, can be ignored
            folder -- a relative path to the folder where the database should be stored
            uid -- the value under which the database stores the user's Primary Key, holdover can be safely ignored
            hashlength -- the length of password hashes

        The system defaults to name="ClassRank.db", table="main" folder="data", uid="user_id, and hashlength="64"
        """
        self.engine = sqlalchemy.create_engine(os.environ['DATABASE_URL'])

        self.base = sqlalchemy.ext.declarative.declarative_base()
        self.metadata = self.base.metadata

        # the three main parts of the overall database system
        self.calculation = CalculationDatabase.CalculationDatabase(self.base).create()
        self.opinion = OpinionDatabase.OpinionDatabase(self.base).create()
        self.similarity = SimilarityDatabase.SimilarityDatabase(self.base).create()

        self.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)

        # on first run, create an admin account

    # the rest is just abstraction to make life less terrible
    @contextmanager
    def session_scope(self):
        """
        database session factory wrapper

        Provide a transactional scope around a series of operations.  use the syntax
            `with Database.session_scope() as session: #or similar`
        for operations requiring a session
        """
        session = self.sessionmaker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    def add_opinion(self, session, user_id, movie_id, rating):
        if not self.opinion_exists(session, item=movie_id, user=user_id):
            session.add(self.opinion(user_id=user_id, item_id=movie_id, rating=rating))
            return True
        return False

    def add_similarity(self, session, user_a, user_b, a, b):
        if not self.similarity_exists(session, usera_id=user_a, userb_id=user_b):
            session.add(self.similarity(usera_id=user_a, userb_id=user_b, a=a, b=b))
            return True
        return False

    def add_calculation(self, session, user, movie, rating):
        if not self.calculation_exists(session, user_id=user, item_id=item):
            session.add(self.calculation(user_id=user, item_id=item, rating=rating))
            return True
        return False


    def opinion_exists(self, session, user=None, item=None):
        try:
            query = {}
            if user:
                query["user_id"] = user
            if item:
                query["item_id"] = item
            session.query(self.opinion).filter_by(**query).one()
            return True
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    def similarity_exists(self, session, usera_id=None, userb_id=None):
        try:
            query = {}
            if usera_id:
                query["usera_id"] = usera_id
            if userb_id:
                query["userb_id"] = userb_id
            session.query(self.similarity).filter_by(**query).one()
            return True
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    def calculation_exists(self, session, user_id=None, item_id=None):
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            if item_id:
                query["item_id"] = item_id
            session.query(self.calculation).filter_by(**query).one()
            return True
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    # methods that do things!
    def fetch_opinion(self, session, user, item):  # done
        try:
            return session.query(self.opinion).filter(self.opinion.user_id == user, self.opinion.item_id == item).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.Opinion, user, item)

    def fetch_similarity(self, session, usera, userb):  # done
        try:
            return session.query(self.similarity).filter(self.similarity.usera_id == usera, self.similarity.userb_id == userb).one()
        except sqlalchemy.orm.exc.ObjectDeletedError:
            raise ItemDoesNotExistError(DatabaseObjects.Similarity, usera, userb)

    def fetch_calculation(self, session, user, item):  # done
        try:
            return session.query(self.calculation).filter(self.calculation.user_id == user, self.calculation.item_id == item).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.Calculation, user, item)

    def remove_opinion(self, session, user, item):  # done, this can be made better
        if self.opinion_exists(session, user, item):
            session.query(self.opinion).filter(self.opinion.user_id == user, self.opinion.item_id == item).delete()

    def remove_similarity(self, session, usera, userb):  # done
        if self.similarity_exists(session, usera, userb):
            sim = session.query(self.similarity).filter(self.similarity.usera_id == usera, self.similarity.userb_id == userb).one()
            session.delete(sim)

    def remove_calculation(self, session, user, item):  # done, this can be made better
        if self.opinion_exists(session, user, item):
            session.query(self.calculation).filter(self.calculation.user_id == user, self.calculation.item_id == item).delete()

    def remove_user(self, session, user):
        try:
            session.query(self.opinion).filter(self.opinion.user_id == user).delete()
            session.query(self.similarity).filter(_or(self.similarity.usera_id == user, self.similarity.userb_id == user))
            session.query(self.calculation).filter(self.calculation.user_id == user).delete()
        except sqlalchemy.exc.SQLAlchemyError:
            raise UserDoesNotExistError(DatabaseObjects.Opinion, user)

    def remove_item(self, session, item):
        try:
            session.query(self.opinion).filter(self.opinion.item_id == item).delete()
            session.query(self.calculation).filter(self.calculation.item_id == item).delete()
        except sqlalchemy.exc.SQLAlchemyError:
            raise ItemDoesNotExistError(DatabaseObjects.Opinion, item)


    def update_opinion(self, session, user, item, rating):
        if self.opinion_exists(session, user, item):
            changes = {}
            changes["rating"] = rating
            session.query(self.opinion).filter(self.opinion.user_id == user, self.opinion.item_id == item).update(changes)

    def update_similarity(self, session, usera, userb, a, b):
        if self.similarity_exists(session, usera, userb):
            changes = {}
            changes["a"] = a
            changes["b"] = b
            session.query(self.similarity).filter(self.similarity.usera_id == usera, self.similarity.userb_id == userb).update(changes)

    def update_calculation(self, session, user, item, rating):
        if self.calculation_exists(session, user, item):
            changes = {}
            changes["rating"] = rating
            session.query(self.calculation).filter(self.calculation.user_id == user, self.calculation.item_id == item).update(changes)

    def __enter__(self):
        """
        syntactic sugar
        """
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        """
        the sugariest of syntaxes
        """
        pass

    @property
    def calculations(self):
        """
        property, all users in the database
        """
        with self.session_scope() as session:
            return session.query(self.calculation).all()

    @property
    def similarities(self):
        """
        property, all moderators in the database
        """
        with self.session_scope() as session:
            return session.query(self.similarity).all()

    @property
    def opinions(self):
        """
        property, all schools in the database
        """
        with self.session_scope() as session:
            return session.query(self.opinion).all()


#A collection of error classes raised when either things do or do not exist in the database
class DatabaseObjects(Enum):
    """
    So enums are beautiful and I love them
    """
    Opinion = "Opinion"
    Similarity = "Similarity"
    Calculation = "Calculation"

class ItemExistsError(Exception):
    """
    Exception raised when an item is already in the database
    """
    def __init__(self, identifier, name, *args):
        self.identifier = identifier
        self.name = name
        self.information = args

    def __str__(self):
        return "A {} named {} already exists".format(self.identifier.name, self.name)


class ItemDoesNotExistError(Exception):
    """
    Exception raised when an item is not in the database
    """
    def __init__(self, identifier, name, *args):
        self.identifier = identifier
        self.name = name
        self.information = args

    def __str__(self):
        return "A {} named {} does not exist".format(self.identifier.name, self.name)

class UserDoesNotExistError(Exception):
    def __init__(self, identifier, name, *args):
        self.identifier = identifier
        self.name = name
        self.information = args

    def _-str__(self):
        return "User {} does not have any opinions".format(self.name)

class ItemDoesNotExistError(Exception):
    def __init__(self, identifier, name, *args):
        self.identifier = identifier
        self.name = name
        self.information = args

    def _-str__(self):
        return "Item {} does not have any opinions".format(self.name)
