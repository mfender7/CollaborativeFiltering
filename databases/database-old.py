"""
A collection of tools to access and work with databases, with the goal of being completely self-contained (ie. all
    database use runs through this api) allowing for easy updates later.

Classes:
    
    Database:
        A database editor
        Methods:
            Connect (automatically) - Connect to an existing database
            Create (automatically)  - create a new database and connect to it
            addUser                 - create a new user (row)
            deleteUser              - remove an existing user from the database
            addItem                 - add a new item (course to be judged) to the database
            currentOpinions         - get all opinions for a user as a tuple
            currentOpinion          - get a user's opinion for a specific item
            changeOpinion           - set a user's opinion for a specific item
            newField                - adds a new Field (column) to the table

    Viewer:
        Like a database, but read-only (also probably caching magicks)
        Methods:
        Connect     - Connect to an existing database
        getOpinions - get all opinions for a user as a tuple
        getOpinion  - get a user's opinion for a specific item

Both the Database and Viewer objects should be completely safe, in that they do everything required to prevent attacks 
    sent to the system by nefarious users (SQL injection, for example) and they implement all required error and edge
    case checking.  In other words, the objects should deal with any errors internally and preferably proactively.
"""

import sqlite3
import os.path


class Database(object):
    """
    A class that can access, read, write, create and generally pretend to be a database.  Currently implemented in SQLite.
    The current implementation uses SQLite, for which there is good documentation here http://www.sqlite.org/

    A quick reference:
        CREATE TABLE if not exists {table_name} ({comma seperated statements}, {representing field type and name}, {ex. INTEGER id})
            creates a new table with a set of columns with the given settings

        PRAGMA table_info({table_name})
            returns ({position}, {name}, {type}, {can be null}, {default}, {is primary key}) for each field in the table

        INSERT INTO {table_name} ({list_of_fields}) VALUES ({list_of_values})
            {list_of_values} should always be "?" and have its value set elswhere to prevent injection

        ALTER TABLE {table_name} ADD {column_name} {type}
            adds {column_name} of type {type} to {table}, possible to set initial values.  This is slow

        SELECT {fields} FROM {table_name} where {field} = {?}
            returns a tuple of the values of fields (which can be wildcard) for each column where {field} is the named 
            value

        UPDATE {table_name} SET {item}=? WHERE {field} = ?
            changes the value of {item} in all rows where {field} is the given value.  Requires a tuple 
            ({new_item}, {field_value}) to work correctly

    Instance Data:
        databaseFolder -> the folder where the database is held
        usernameField  -> the field name for "username", the string representation of a user
        uniqueID       -> the field name for the primary key value
        name           -> the name of the database file
        table          -> the name of the active table in the database file
        path           -> the relative path to the database, including the database name
        tableLength    -> the number of opinion fields in the table
        db             -> the sqlite3 database object
        cursor         -> the sqlite3 cursor object
        columnInfo     -> ({position}, {name}, {type}, {can be null}, {default}, {is primary key}) for each field in the
                            table
    """

    
    def __init__(self, name="database.db", table="main", folder="data", uid="id"):
        """
        Looks for a database of the given name.  If it exists, connects to it.  Otherwise, creates it and then connects
            to it.

        Arguments:
            name   -> the name of the database file
            table  -> the name of the table to be used
            folder -> path to the folder in which the database is stored, can be "."
        """

        #initialize values
        self.databaseFolder = folder
        self.usernameField = "username"
        self.uniqueID = uid
        self.name = name
        self.table = table
        self.path = os.path.join(self.databaseFolder,self.name)
        self.columnInfo = []

        #check to see if database exists, if yes, connect to it, if no, create and then connect to it
        if (os.path.isfile(self.path)):
            self._connect()
        else:
            self._create()
            self._connect()

        self.tableLength = len(self.columnInfo) - 2


    def _create(self):
        """
        Creates a table of the provided name if necessary, creates two columns in the table:
            username, which represents the name of the user
            id, a unique primary key for each user
        """

        db = sqlite3.connect(self.path)
        cursor = db.cursor()

        cursor.execute('''CREATE TABLE if not exists {table} ({id} INTEGER PRIMARY KEY AUTOINCREMENT, {username} TEXT)'''
            .format(table = self.table, id = self.uniqueID, username = self.usernameField))

        db.commit()
        db.close()


    def _connect(self):
        """
        Establishes a connection to the table and sets the .db and .cursor values which are global for the database
        object.
        """

        self.db = sqlite3.connect(self.path)
        self.cursor = self.db.cursor()

        self.columnInfo = [x for x in self.cursor.execute('''PRAGMA table_info({table})'''.format(table=self.table))]

    def items(self):
        """
        returns a list of tuples in the format ({field_name}, {data_format}) for each field/column in the table
        """
        self.columnInfo = [x for x in self.cursor.execute('''PRAGMA table_info({table})'''.format(table=self.table))]
        return zip(*zip(*self.columnInfo)[1:3])[2:]


    def addUser(self, name):
        """
        Checks to see if a user of the given name exists.  If they do, do nothing.  If they don't, create a new user of
            the new name

        Arguments:
            name -> the username of the new user
        """

        if name not in self:
            self.cursor.execute('''INSERT INTO {table} ({fields}) VALUES ({insertions})'''
                .format(table = self.table, insertions = self._questionMarks(), fields = self._fields()), 
                self._insertions(name))
            self.db.commit()


    def _questionMarks(self):
        """
        Helper method that creates a comma seperated list of question marks for SQL parameterization.  The number of
            question marks is 1 for username + the number of additional columns.  This is sloppy.
        """
        return ",".join("?" for x in xrange(self.tableLength+1))


    def _insertions(self, name):
        """
        Returns a tuple in the format ({username},None,...None) where None is repeated for each non-username field in
            the table
        """
        return (name,) + tuple(None for x in xrange(self.tableLength))


    def _fields(self):
        """
        Returns a comma seperated string of the fields in the table, useful for "INSERT INTO {table} ({fields})"
        """
        return ",".join(list(zip(*self.columnInfo)[1])[1:])


    def newField(self, column, datatype="integer"):
        """
        Adds a new column (For a new course) to the table, if it does not exist
        """

        if column not in list(zip(*self.columnInfo)[1])[1:]:
            self.cursor.execute('''ALTER TABLE {table} ADD {column} {type}'''
                .format(table = self.table, type = datatype, column = column))
            self.db.commit()


    def deleteUser(self, name):
        """
        Removes a user (row) from the database
        """
        pass


    def currentOpinions(self, name):
        """
        Returns all of the opinions of a given user as a tuple
        """
        self.cursor.execute('''SELECT * FROM {table} where {username} = ? '''
            .format(table = self.table, username = self.usernameField), (name,))
        return self.cursor.fetchone()[2:]


    def currentOpinion(self, user, item):
        """
        Returns the opinion of a user for a single item
        """
        self.cursor.execute('''SELECT {item} FROM {table} where {username} = ? '''
            .format(table = self.table, username = self.usernameField, item = item), (user,))
        return self.cursor.fetchone()[0]


    def changeOpinion(self, user, item, value):
        """
        Sets the value of an item for a single user
        """
        self.cursor.execute('''UPDATE {table} SET {item}=? WHERE {username} = ? '''
            .format(table = self.table, fields = self._fields(), username = self.usernameField, item=item), 
            tuple([value,user]))
        self.db.commit()

    def users(self):
        """
        returns a list of usernames
        """
        return [name for name in self.cursor.execute('''SELECT {username} FROM {table}'''
            .format(table = self.table, username = self.usernameField))]
    

    def __contains__(self, user):
        """
        For an user returns True if an item of that name is in the table, otherwise returns False
        """
        
        self.cursor.execute('''SELECT * FROM {table} where {username} = ?'''
            .format(table = self.table, username = self.usernameField), (user,))
        if self.cursor.fetchone() == None:
            return False
        else:
            return True



def Viewer(name="database.db", table="main", folder="data"):
    """
    Helper function for implementing a database viewer, makes certain that the file exists
    """
    if (os.path.isfile(os.path.join(folder, name))):
        return _Viewer(name, table, folder)
    else:
        raise IOError


class _Viewer(object):
    """
    A readonly database instance
    """

    def __init__(self, name="database.db", table="main", folder="data"):
        self.databaseFolder = folder
        self.usernameField = "username"
        self.uniqueID = "id"
        self.name = name
        self.table = table
        self.path = os.path.join(self.databaseFolder,self.name)
        self._connect()

    def _connect(self):
        """
        Establishes a connection to the table and sets the .db and .cursor values
        """

        self.db = sqlite3.connect(self.path)
        self.cursor = self.db.cursor()

        self.columnInfo = [x for x in self.cursor.execute('''PRAGMA table_info({table})'''.format(table=self.table))]

    def items(self):
        """
        returns a list of tuples in the format ({field_name}, {data_format}) for each field/column in the table
        """
        self.columnInfo = [x for x in self.cursor.execute('''PRAGMA table_info({table})'''.format(table=self.table))]
        return zip(*zip(*self.columnInfo)[1:3])[2:]

    def currentOpinions(self, name):
        """
        Returns all of the opinions of a given user as a tuple
        """
        self.cursor.execute('''SELECT * FROM {table} where {username} = ? '''
            .format(table = self.table, username = self.usernameField), (name,))
        return self.cursor.fetchone()[2:]


    def currentOpinion(self, user, item):
        """
        Returns the opinion of a user for a single item
        """
        self.cursor.execute('''SELECT {item} FROM {table} where {username} = ? '''
            .format(table = self.table, username = self.usernameField, item = item), (user,))
        return self.cursor.fetchone()[0]


    def changeOpinion(self, user, item, value):
        """
        Sets the value of an item for a single user
        """
        self.cursor.execute('''UPDATE {table} SET {item}=? WHERE {username} = ? '''
            .format(table = self.table, fields = self._fields(), username = self.usernameField, item=item), 
            tuple([value,user]))
        self.db.commit()
    

    def _fields(self):
        """
        Returns a comma seperated string of the fields in the table, useful for "INSERT INTO {table} ({fields})"
        """
        return ",".join(list(zip(*self.columnInfo)[1])[1:])


    def users(self):
        """
        returns a list of usernames
        """
        return [name for name in self.cursor.execute('''SELECT {username} FROM {table}'''
            .format(table = self.table, username = self.usernameField))]


    def __contains__(self, user):
        """
        For an user returns True if an item of that name is in the table, otherwise
            returns False
        """
        
        self.cursor.execute('''SELECT * FROM {table} where {username} = ?'''
            .format(table = self.table, username = self.usernameField), (user,))
        if self.cursor.fetchone() == None:
            return False
        else:
            return True



if __name__ == "__main__":
    database = Database()
    viewer = Viewer()
    database.addUser("one")
    database.addUser("two")
    database.addUser("three")
    database.addUser("four")
    database.newField("CS1331")
    database.newField("CS1332")
    database.newField("CS1333")
    database.newField("CS1334")
    database.newField("CS1335")
    users = ["one", "two", "three", "four"]
    classes = ["CS1331", "CS1332", "CS1333", "CS1334"]
    vals = [1,2,3,5,1,0,3,5,1,1,1,1,5,5,5,5]

    counter = 0
    for user in users:
        for eachClass in classes:
            database.changeOpinion(user, eachClass, vals[counter])
            counter += 1

    for user in users:
        for eachClass in classes:
            assert database.currentOpinion(user, eachClass) == database.currentOpinion(user, eachClass)





