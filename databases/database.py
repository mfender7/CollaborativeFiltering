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
from . import CalculationDatabase
from . import OpinionDatabase
from . import SimilarityDatabase
import time  # for creating hash salts
import scrypt  # for hashing passwords
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

    def __init__(self, name="ClassRank.db", folder="data", hashlength=64):
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

        self.hashlength = hashlength  # length of the scrypt password hash
        self.base = sqlalchemy.ext.declarative.declarative_base()
        self.metadata = self.base.metadata

        # the three main parts of the overall database system
        self.course = CalculationDatabase.CalculationDatabase(self.base).create()
        self.rating = OpinionDatabase.OpinionDatabase(self.base).create()
        self.user = SimilarityDatabase.SimilarityDatabase(self.base).create()

        self.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)

        # on first run, create an admin account
        if len(self.schools) == 0:
            with self.session_scope() as session:
                self.add_school(session, "Admin Academy", "Admin")
                self.add_user(session, "Admin", "admin@admin.admin", "password", "Admin", admin=True, mod=True)

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

    # methods that do things!
    def fetch_school_by_name(self, session, school_name):  # done
        """
        """
        try:
            return session.query(self.school).filter(self.school.school_short == school_name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.School, school_name)

    def fetch_school_by_id(self, session, schoolid):  # done
        """
        """
        try:
            return session.query(self.school).get(schoolid)
        except sqlalchemy.orm.exc.ObjectDeletedError:
            raise ItemDoesNotExistError(DatabaseObjects.School, schoolid)

    def fetch_user_by_name(self, session, user):  # done
        """
        """
        try:
            return session.query(self.user).filter(self.user.user_name == user).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.User, user)

    def fetch_user_by_id(self, session, userid):  # done
        """
        """
        try:
            return session.query(self.user).get(userid)
        except sqlalchemy.orm.exc.ObjectDeletedError:
            raise ItemDoesNotExistError(DatabaseObjects.User, userid)

    def fetch_course_by_name(self, session, school, coursename, semester=None, year=None, professor=None):  # done, might want to clean it
        """
        """
        try:
            schoolid = session.query(self.school).filter(self.school.school_short == school).one().school_id
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.School, school)

        query = {}
        query["identifier"] = coursename
        query["school_id"] = schoolid

        if semester:
            query["semester"] = semester
        if year:
            query["year"] = year
        if professor:
            query["professor"] = professor

        try:
            return session.query(self.course).filter_by(**query).one()
        except:
            raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)

    def fetch_course_by_id(self, session, courseid):  # done
        """
        """
        try:
            return session.query(self.course).get(courseid)
        except sqlalchemy.orm.exc.ObjectDeletedError:
            raise ItemDoesNotExistError(DatabaseObjects.Course, courseid)

    def fetch_rating_by_name(self, session, username, coursename, semester=None, year=None, professor=None):  # done
        """
        """
        try:
            user = session.query(self.user).filter(self.user.user_name == username).one()
            userid = user.user_id
            schoolid = user.school_id
        except:
            raise ItemDoesNotExistError(DatabaseObjects.User, username)

        try:
            schoolname = self.fetch_school_by_id(session, schoolid).school_short
            courseid = self.fetch_course_by_name(session, schoolname, coursename, semester=semester, year=year, professor=professor).course_id
        except:
            raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)

        try:
            return session.query(self.rating).filter(self.rating.user_id == userid, self.rating.course_id == courseid).one()
        except:
            raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)

    def fetch_rating_by_id(self, session, userid, courseid):  # done
        """
        """
        try:
            return session.query(self.rating).filter(self.rating.user_id == userid).filter(self.rating.course_id == courseid).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.Rating, str(userid)+" for "+str(courseid))

    def school_exists(self, session, school_name=None, school_id=None, school_short=None):  # done
        """
        """
        try:
            query = {}
            if school_name:
                query["school_name"] = school_name
            if school_id:
                query["school_id"] = school_id
            if school_short:
                query["school_short"] = school_short
            session.query(self.school).filter_by(**query).one()
            return True
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    def user_exists(self, session, user_name=None, user_id=None, email_address=None):  # done
        """
        """
        try:
            query = {}
            if user_name:
                query["user_name"] = user_name
            if user_id:
                query["user_id"] = user_id
            if email_address:
                query["email_address"] = email_address
            session.query(self.user).filter_by(**query).one()
            return True
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    def course_exists(self, session, coursename=None, course_id=None, school=None, school_id=None, semester=None, year=None, professor=None):  # done
        """
        """
        try:
            query = {}
            query["identifier"] = coursename
            if semester:
                query["semester"] = semester
            if year:
                query["year"] = year
            if professor:
                query["professor"] = professor
            if course_id:
                query["course_id"] = course_id
            if school:
                query["school_id"] = self.fetch_school_by_name(session, school).school_id
            if school_id:
                query["school_id"] = school_id
            session.query(self.course).filter_by(**query).one()
            return True
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    def rating_exists(self, session, username, coursename, semester=None, year=None, professor=None):  # done
        if self.user_exists(session, user_name=username):
            user = self.fetch_user_by_name(session, username)
            userid = user.user_id
            schoolid = user.school_id
            schoolname = self.fetch_school_by_id(session, schoolid).school_short
        else:
            return False
        if self.course_exists(session, school_id=schoolid, coursename=coursename, semester=semester, year=year, professor=professor):
            courseid = self.fetch_course_by_name(session, schoolname, coursename, semester=semester, year=year, professor=professor).course_id
        else:
            return False
        try:
            self.fetch_rating_by_id(session, userid, courseid)
            return True
        except ItemDoesNotExistError:
            return False

    def add_school(self, session, school_name, school_identifier):  # done
        if not self.school_exists(session, school_short=school_identifier):
            session.add(self.school(school_name=school_name, school_short=school_identifier))
            return True
        return False

    def add_user(self, session, username, email, password, school, first=None, last=None, admin=False, mod=False):  # done
        if not self.user_exists(session, user_name=username):
            salt = str(int(time.time()))
            pwhash = b64encode(scrypt.hash(password, salt, self.hashlength))
            apikey = hashlib.sha256(pwhash).hexdigest()
            if self.school_exists(session, school_short=school):
                schoolid = self.fetch_school_by_name(session, school).school_id
                session.add(self.user(user_name=username, email_address=email, password_hash=pwhash, password_salt=salt, school_id=schoolid, first_name=first, last_name=last, admin=admin, moderator=mod, apikey=apikey))
                return True
            return False

    def add_course(self, session, school, coursename, identifier, professor=None, year=None, semester=None):  # done
        if not self.course_exists(session, school=school, coursename=identifier, professor=professor, year=year, semester=semester):
            if self.school_exists(session, school_short=school):
                schoolid = self.fetch_school_by_name(session, school).school_id
                session.add(self.course(course_name=coursename, school_id=schoolid, identifier=identifier, professor=professor, year=year, semester=semester))
                return True
        return False

    def add_rating(self, session, username, coursename, semester=None, year=None, professor=None, rating=None, grade=None, difficulty=None):  # done
        if not self.rating_exists(session, username, coursename, semester=semester, year=year, professor=professor):
            user = self.fetch_user_by_name(session, username)
            userid = user.user_id
            schoolname = self.fetch_school_by_id(session, user.school_id).school_short
            courseid = self.fetch_course_by_name(session, schoolname, coursename, semester=semester, year=year, professor=professor).course_id
            session.add(self.rating(user_id=userid, course_id=courseid, semester=semester, year=year, professor=professor, rating=rating, grade=grade, difficulty=difficulty))

            return True
        return False

    def remove_rating(self, session, username, coursename, semester=None, year=None, professor=None):  # done, this can be made better
        if self.rating_exists(session, username, coursename, semester=semester, year=year, professor=professor):
            user = self.fetch_user_by_name(session, username)
            userid = user.user_id
            schoolid = user.school_id
            schoolname = self.fetch_school_by_id(session, schoolid).school_short
            courseid = self.fetch_course_by_name(session, schoolname, coursename=coursename, semester=semester, year=year, professor=professor).course_id
            session.query(self.rating).filter(self.rating.user_id==userid, self.rating.course_id==courseid).delete()

    def remove_user(self, session, username):  # done
        if self.user_exists(session, username):
            user = session.query(self.user).filter(self.user.user_name==username).one()
            session.delete(user)

    # neither schools nor courses can be removed

    def update_user(self, session, username, email_address=None, first=None, last=None, age=None, graduation=None, admin=None, mod=None):  # done
        if self.user_exists(session, username):
            changes = {}
            if email_address:
                changes["email_address"] = email_address
            if first:
                changes["first_name"] = first
            if last:
                changes["last_name"] = last
            if age:
                changes["age"] = age
            if graduation:
                changes["graduation"] = graduation
            if admin:
                changes["admin"] = admin
            if mod:
                changes["mod"] = mod

            session.query(self.user).filter(self.user.user_name==username).update(changes)

    def update_course(self, session, school, coursename, oldsem=None, oldyear=None, oldprof=None, identifier=None, semester=None, year=None, professor=None):  # done
        if self.course_exists(session, school=school, coursename=coursename, semester=oldsem, year=oldyear, professor=oldprof):
            courseid = self.fetch_course_by_name(session, school, coursename, semester=oldsem, year=oldyear, professor=oldprof).course_id
            changes = {}
            if identifier:
                changes["identifier"] = identifier
            if semester:
                changes["semester"] = semester
            if year:
                changes["year"] = year
            if professor:
                changes["professor"] = professor

            session.query(self.course).filter(self.course.course_id==courseid).update(changes)

    def update_rating(self, session, username, coursename, oldsem=None, oldyear=None, oldprof=None, semester=None, year=None, professor=None, rating=None, grade=None, difficulty=None):  # done
        if self.rating_exists(session, username, coursename, semester=oldsem, year=oldyear, professor=oldprof):
            rated = self.fetch_rating_by_name(session, username, coursename, semester=oldsem, year=oldyear, professor=oldprof)
            userid = rated.user_id
            courseid = rated.course_id
            changes = {}
            if semester:
                changes["semester"] = semester
            if year:
                changes["year"] = year
            if professor:
                changes["professor"] = professor
            if rating:
                changes["rating"] = rating
            if grade:
                changes["grade"] = grade
            if difficulty:
                changes["difficulty"] = difficulty

            session.query(self.rating).filter(self.rating.course_id==courseid, self.rating.user_id==userid).update(changes)


    def fetch_students(self, session, school):
        """
        """
        pass

    def fetch_courses(self, session, user):
        """
        """
        pass

    def update_password(self, session, username, new_password):
        """
        """
        if self.user_exists(session, user_name=username):
            user = self.fetch_user_by_name(session, username)
            newsalt = str(int(time.time()))
            newhash = b64encode(scrypt.hash(new_password, newsalt, self.hashlength))
            user.password_hash = newhash
            user.password_salt = newsalt
            return True
        return False

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
    def users(self):
        """
        property, all users in the database
        """
        with self.session_scope() as session:
            return session.query(self.user).all()

    @property
    def moderators(self):
        """
        property, all moderators in the database
        """
        with self.session_scope() as session:
            return session.query(self.user).filter(self.user.moderator == True).all()


    @property
    def admins(self):
        """
        property, all administrators in the database
        """
        with self.session_scope() as session:
            return session.query(self.user).filter(self.user.admin == True).all()


    @property
    def schools(self):
        """
        property, all schools in the database
        """
        with self.session_scope() as session:
            return session.query(self.school).all()

    @property
    def ratings(self):
        with self.session_scope() as session:
            return session.query(self.rating).all()


    @property
    def courses(self):
        """
        property, all courses in the db
        """
        with self.session_scope() as session:
            return session.query(self.course).all()


#A collection of error classes raised when either things do or do not exist in the database
class DatabaseObjects(Enum):
    """
    So enums are beautiful and I love them
    """
    School = "School"
    User = "User"
    Course = "Course"
    Rating = "Rating"


class Semesters(Enum):
    """
    """
    Spring = "Spr"
    Summer = "Sum"
    Fall = "Fall"
    Winter = "Win"


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

class PasswordLengthError(Exception):
    """
    Exception raised when a user's password is too long (hashing 2000 char passwords is bad)
    """
    def __init__(self, user, password):
        self.password = password
        self.user = user

    def str(self):
        return "User {}'s password ({}) is too long".format(self.user, self.password)
