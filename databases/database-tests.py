
import unittest
import os
import database
import sqlalchemy.ext
import scrypt



class DatabaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            os.remove("./data/Testdb.db")
        except FileNotFoundError as e:
            pass

    def setUp(self):
        """
        instantiates the test database
        """
        self.db = database.Database(name="Testdb.db", folder="data")

    def test_01_remove(self):
        """
        tests creating and deleting an empty database
        """
        self.assertTrue(self.db)
        with self.db.session_scope() as session:
            #you can operate on an empty database
            self.assertFalse(self.db.school_exists(session, school_short="Georgia Tech"))

        os.remove("./data/Testdb.db")  # hard remove the database file (this should never happen)
        self.assertTrue(self.db)
        with self.db.session_scope() as session:
            #when the database doesn't exist, shit breaks yo
            self.assertRaises(sqlalchemy.exc.OperationalError, self.db.school_exists, session, {"school_short":"Georgia Tech"})

    def test_02_add_schools(self):
        #establish a connection
        with self.db.session_scope() as session:
            self.assertFalse(self.db.school_exists(session, "Georgia Tech"))
        
        #establish another connection 
        #this tests that connections are created/ended correctly 
        with self.db.session_scope() as session:
            #make some schools to use later
            self.db.add_school(session, school_name="Georgia Institute of Technology", school_identifier="Georgia Tech")
            self.db.add_school(session, school_name="Harvard University", school_identifier="Harvard")
            self.db.add_school(session, school_name="This is a hilariously long name that is longer than anything in productin !@#$%^&*()_+", school_identifier="!@#$%^&*()_+ also way longer than anything irl")

        with self.db.session_scope() as session:
            #check that the fetch_school and school_exists work
            self.assertTrue(self.db.school_exists(session, school_name="Georgia Institute of Technology"))
            self.assertTrue(self.db.school_exists(session, school_short="Georgia Tech"))
            self.assertTrue(self.db.school_exists(session, school_id=3))
            self.assertEqual(self.db.fetch_school_by_name(session, "Georgia Tech").school_name, "Georgia Institute of Technology")
            self.assertEqual(self.db.fetch_school_by_id(session, 1).school_name, "Georgia Institute of Technology")
            self.assertRaises(database.ItemDoesNotExistError, self.db.fetch_school_by_name, session, "help me")

    def test_03_add_users(self):
        with self.db.session_scope() as session:
            self.assertFalse(self.db.user_exists(session, "jmorton"))

        with self.db.session_scope() as session:
            #shows that a complex user can be added
            self.assertTrue(self.db.add_user(session, "jmorton", "joshua.morton@gatech.edu", "password", "Georgia Tech", first="Joshua", last="Morton", admin=True, mod=True))
            #as well as a simple one
            self.db.add_user(session, "cmalan", "malanMan@harvard.edu", "CS50isTheBest", "Harvard", mod=True)
            #but that they need to attend a real school
            self.assertFalse(self.db.add_user(session, "fake_user", "fmail", "fake_pw", "fakeuni"))

        with self.db.session_scope() as session:
            #checks that users can be searched
            self.assertTrue(self.db.user_exists(session, user_name="jmorton"))
            self.assertTrue(self.db.user_exists(session, email_address="malanMan@harvard.edu"))
            self.assertTrue(self.db.user_exists(session, user_id=1))
            #shows that even when correct information from conflicting users is provided, the result is correct
            self.assertFalse(self.db.user_exists(session, user_name="jmorton", email_address="malanMan@harvard.edu"))
            self.assertEqual(self.db.fetch_user_by_name(session, "jmorton").first_name, "Joshua")
            #and nonexistant users throw errors
            self.assertRaises(database.ItemDoesNotExistError, self.db.fetch_user_by_name, session, "name")
            #hashes are not the same as passwords
            self.assertNotEqual(self.db.fetch_user_by_name(session, "jmorton").password_hash, "password")
            #and we can authenticate users from them
            tempuser = self.db.fetch_user_by_name(session, "jmorton")
            self.assertEqual(tempuser.password_hash, scrypt.hash("password", tempuser.password_salt, self.db.hashlength))

    def test_04_add_courses(self):
        with self.db.session_scope() as session:
            self.assertFalse(self.db.course_exists(session, coursename="CS1301"))

        with self.db.session_scope() as session:
            #you can add a course
            self.db.add_course(session, "Georgia Tech", "Introduction to Computer Science in Python", "CS1301")
            #and a similar one that is more complex
            self.assertTrue(self.db.add_course(session, "Georgia Tech", "Introduction to Computer Science in Python", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Fall.value))
            self.assertFalse(self.db.course_exists(session, school="Georgia Tech", coursename="CS1301", professor="Summet", year=2013, semester=database.Semesters.Spring.value))
            #and similar courses differing only in semester
            self.assertTrue(self.db.add_course(session, "Georgia Tech", "Introduction to Computer Science in Python", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Spring.value))

        with self.db.session_scope() as session:
            #two courses that are similar are not the same
            self.assertNotEqual(self.db.fetch_course_by_name(session, "Georgia Tech", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Fall.value), 
                self.db.fetch_course_by_name(session, "Georgia Tech", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Spring.value))
            #and furthermore, there are more than 2 couses, meaning things are different
            self.assertGreater(len(self.db.courses), 2)
            self.assertTrue(self.db.course_exists(session, school="Georgia Tech", coursename="CS1301", professor="Summet", year=2013, semester=database.Semesters.Fall.value))
        
        with self.db.session_scope() as session:
            #add additional courses to things
            self.db.add_course(session, "Harvard", "Introduction to Computer Science in C", "CS50", professor="Malan", year=2012, semester=database.Semesters.Fall.value)    
            self.db.add_course(session, "Georgia Tech", "Health", "APPH1040")

    def test_05_add_ratings(self):
        with self.db.session_scope() as session:
            #returns false if the rating doesn't exist
            self.assertFalse(self.db.rating_exists(session, "jmorton", "APPH1040"))
            #also fails gracefully if the course or school doesn't exist, or if they don't match
            self.assertFalse(self.db.rating_exists(session, "nonexistant user", "CS50", professor="Malan", year=2012, semester=database.Semesters.Fall.value))
            self.assertFalse(self.db.rating_exists(session, "jmorton", "fake course"))
            self.assertFalse(self.db.rating_exists(session, "jmorton", "CS50", professor="Malan", year=2012, semester=database.Semesters.Fall.value))

        with self.db.session_scope() as session:
            #adding a rating fails by throwing an error if school & user do not "match"
            self.assertRaises(database.ItemDoesNotExistError, self.db.add_rating, session, "jmorton", "CS50", semester=database.Semesters.Fall.value, year=2012, professor="Malan", rating=5, grade=5, difficulty=5)
            #but you can do it
            self.assertTrue(self.db.add_rating(session, "jmorton", "CS1301", semester=database.Semesters.Fall.value, year=2013,   professor="Summet", rating=5, grade=5, difficulty=2))
            self.assertTrue(self.db.add_rating(session, "cmalan", "CS50", semester=database.Semesters.Fall.value, year=2012, professor="Malan", rating=5, grade=5, difficulty=5))
            self.assertTrue(self.db.add_rating(session, "jmorton", "APPH1040", rating=3, grade=3, difficulty=4))

        with self.db.session_scope():
            #look, ratings exist!
            self.assertTrue(self.db.rating_exists(session, "jmorton", "CS1301", semester=database.Semesters.Fall.value, year=2013, professor="Summet"))

    def test_06_updates(self):
        with self.db.session_scope() as session:
            #update a password
            oldpw = self.db.fetch_user_by_name(session, "jmorton")
            self.db.update_password(session, "jmorton", "password2")
            oldmalanpw = self.db.fetch_user_by_name(session, "cmalan")
            self.db.update_password(session, "cmalan", "CS50isTheBest")

        #change a password
        with self.db.session_scope() as session:
            #the new and old hashes aren't the same
            self.assertNotEqual(self.db.fetch_user_by_name(session, "jmorton").password_hash, oldpw)
            #also, even if the password is changed to the same thing, the new hash is different because of salting
            self.assertNotEqual(self.db.fetch_user_by_name(session, "cmalan").password_hash, oldmalanpw)

        #update user information
        with self.db.session_scope() as session:
            age = self.db.fetch_user_by_name(session, "jmorton").age
            #you can change arbitrary user info
            self.db.update_user(session, "jmorton", age=18, graduation=2017)
            self.assertNotEqual(age, self.db.fetch_user_by_name(session, "jmorton").age)
            self.db.update_user(session, "cmalan", email_address="Malan@harvard.edu")

        #update course information
        with self.db.session_scope() as session:
            itsid = self.db.fetch_course_by_name(session, "Georgia Tech", "CS1301", semester=database.Semesters.Fall.value, year=2013, professor="Summet").course_id
            self.db.update_course(session, "Georgia Tech", "CS1301", oldsem=database.Semesters.Fall.value, oldyear=2013, oldprof="Summet", professor="Leahy")

        with self.db.session_scope() as session:
            #the course is changes
            self.assertEqual("Leahy", self.db.fetch_course_by_name(session, "Georgia Tech", "CS1301", semester=database.Semesters.Fall.value, year=2013, professor="Leahy").professor)
            self.assertEqual(itsid, self.db.fetch_course_by_name(session, "Georgia Tech", "CS1301", semester=database.Semesters.Fall.value, year=2013, professor="Leahy").course_id)

        #update ratings
        with self.db.session_scope() as session:
            self.db.update_rating(session, "jmorton", "CS1301", oldsem=database.Semesters.Fall.value, oldyear=2013, oldprof="Leahy", rating=1, grade=1, difficulty=1)

        with self.db.session_scope() as session:
            self.assertEqual(self.db.fetch_rating_by_name(session, "jmorton", "CS1301", semester=database.Semesters.Fall.value, year=2013, professor="Leahy").rating, 1)

    def test_07_deletes(self):
        #you can remove a rating
        with self.db.session_scope() as session: 
            self.db.remove_rating(session, "jmorton", "CS1301", semester=database.Semesters.Fall.value, year=2013, professor="Leahy")
            pass

        #you can remove users, and things propgate correctly
        with self.db.session_scope() as session:
            self.db.remove_user(session, "jmorton")
            self.db.remove_user(session, "cmalan")

        self.assertEqual(len(self.db.ratings), 0)

    def test_08_misc(self):
        pass

if __name__ == "__main__":
    unittest.main(verbosity=2)

