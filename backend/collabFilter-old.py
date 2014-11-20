"""
The collaborative filtering portion of the system.
Should always be used with databases.database
"""

import math

import databases.database as databases
import math
import sys

class CollaborativeFilter:
    """
    A Collaborative Filtering algorithm/object meant to be heavily optimized for speed
    """

    def __init__(self, database, table, folder):
        """
        Initializes the db and dbviewer (kinda redundant) objects and the 3 caches for each database.
        The system works a bit like this:
        the collaborative filtering code can be divided up into 3 steps, 

        the first is finding current opinions, this is done from self.opinions if possible and then from the database.

        next, you find the similarities between any set of users.  If they are cached, they are taken from self.similarities,
            otherwise they are gathered by using self._calculateSimilarities

        finally, you calculate the rating that a person has for a given object.  This is stored in self.cache, or if needed
            calculated from self.calculateOpinion, this is the one that mot people will be interfacing with

        Arguments:
            database -> the name of the database file
            table    -> the name of the table in the database file
            folder   -> the system path from this file to the database file
        """
        self.dbViewer = databases.Viewer(database, table, folder)
        self.db = databases.Database(database, table, folder)
        
        #cache is a dictionary in the form {username:dictionary{item:value}}
        #in short, a limited version of the larger table
        #it might behove me to update the weights to its own object that keeps track of active users and stores information
        #only relevant to them, periodically purging itsself.
        self.cache = {}

        #similarities is a dictionary in the form {username:dictionary{username:(similarity between user x and y)}}
        #also might behove to rewrite this as an object that clears itsself overtime and does stuff based on active users
        self.similarities = {}

        #opinions is a dictionary in the form {username:dictionary{item:(predicted opinion of item by user)}}
        self.opinions = {}

    def calculateOpinion(self, user, item):
        """
        returns the opinion a user has for an item (as a float) based on the opinions of other users and their weighted similarities
        """

        if user not in self.opinions:
            self.opinions[user] = {}
        if item not in self.opinions[user]:
            users = {person[0] for person in self.dbViewer.users()} - {user}
            self.opinions[user][item] = self._k(user, users) * sum(self._calculateSimilarities(user, other) * self._fetchOpinion(other, item) for other in users)
        return self.opinions[user][item]

    def _k(self, user, users):
        """
        Calculates the k value (1/ sum(similarities)) for the user whose opinion we are finding
        """
        return 1.0 / sum(self._calculateSimilarities(user, other) for other in users)

    def _calculateSimilarities(self, user, other):
        """
        Calculates the similarity between to users via the fitness function cos(vec(x), vec(y)):
        (sum[for i in the list of Items shared by users x and y](rating of x for i * rating of y for i))/((rss of rating(i) for i by x) * (rss of rating(i) for i by y)
        where rss is the root sum squared computed by sqrt(sum[for i in the list of Items rated by user u](rating of i by u)**2)
        see cos.png
        """

        if user not in self.similarities:
            self.similarities[user] = {}

        if other not in self.similarities[user]:
            items = [column[0] for column in self.dbViewer.items()]
            sharedItems = {item for item in items if self.dbViewer.currentOpinion(user,item) is not None} & {item for item in items if self.dbViewer.currentOpinion(other,item) is not None}
            opinionSum = sum(self._fetchOpinion(user, item) * self._fetchOpinion(other, item) for item in sharedItems)
            self.similarities[user][other] = opinionSum / (self._rss(user, sharedItems) * self._rss(other, sharedItems))
        return self.similarities[user][other]


    def _rss(self, user, shared):
        """
        calculates the root sum squared of a number of values (in this case user opinions), used in calculating the k value
        that is in pseudopython, sqrt(sum((x**2) for x in user.opinions))
        """
        return math.sqrt(sum(self._fetchOpinion(user, item) ** 2 for item in shared))

    def _fetchOpinion(self, user, item):
        """
        for a given user, finds their opinion of an item in the database or cache.
        """
        if user in self.cache:
            return self.cache[user][item]
        else:
            items = (column[0] for column in self.dbViewer.items())
            self.cache[user] = {item: self.dbViewer.currentOpinion(user, item) for item in items}
            return self.cache[user][item]
        





if __name__ == "__main__":
    assert 1 == 1
    #do more
    x = CollaborativeFilter("database.db", "main", "databases/data")
    assert x.dbViewer.name == x.db.name
    users = ["one", "two", "three", "four"]
    classes = ["CS1331", "CS1332", "CS1333", "CS1334"]
    for user in users:
        for clazz in classes:
            sys.stdout.write(user+" "+clazz+" - "+str(x.calculateOpinion(user, clazz))+"\n")