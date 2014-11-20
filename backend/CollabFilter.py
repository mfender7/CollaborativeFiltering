"""
The collaborative filtering portion of the system.
"""


import databases.database as databases
from math import sqrt
from sys import stdout

class CollaborativeFilter(object):
    """
    A Collaborative Filtering algorithm/object meant to be heavily optimized 
    for speed
    """

    def __init__(self, name, path, table, debug=False, cache=True):
        """
        Initilialies the collaborative filter with the values

        Arguments:
            name  -> the name of the database file
            path  -> the path to the database file
            table -> the name of the table in the database file
            debug -> activates debug mode, providing additional outputs and
                     information about what is happening
            cache -> used for testing, to compare between the caches being used
                     and a normal, cache free version both for benchmarking and
                     for error checking
        """

        self.name = name
        self.path = path
        self.table = table
        self.debug = debug
        self.cache = cache
        self.db = databases.Database(self.name, self.table, self.path)

        #implemented as map(user->map(item->opinion))
        #opinions can be None or 1-5
        self.opinions = {}

        #implemented as map(user1->map(user2->tuple(rss(u1), rss(u2), multSum(u1, u2))))
        #rss(u) is root sum squared
        #multSum(u1, u2) is sum(u1[item]*u2[item] for item in sharedItems)
        self.similarities = {}

        #implemented as map(user1->map(item->tuple(sum(simil*opinions[user][item] for user in users), sum(simil for user in users))))
        self.calculated = {}


    def items(self):
        """
        Returns the items in the matrix

        Return -> the list of items
        """
        return self.db.items()

    def users(self):
        """
        Returns the users in the database

        Return -> The users as a list
        """
        return self.db.users();

    def fetchOpinion(self, user, item): #done
        """
        Directly fetches an opinion from the database
        
        Arguments:
            user -> the user who has an opinion
            item -> the item of which they have an opinion

        Return -> a value representing the user's opinion of the item, or none if the user has no opinion
        """

        return self.db.currentOpinion(user, item)


    def predictOpinion(self, user, item): #done except for when the cache is disabled
        """
        Calculates a user's opinion of an item based on the collaborative filtering algorithm.  Uses caches if possible
            and falls back to the long method of calculation if necessary

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion

        Return -> the opinion that a user should have for an item based on collaborative filtering
        """

        if self.cache == True:
            if user not in self.calculated:
                self.calculated[user] = {}
            if item not in self.calculated[user]:
                self.calculated[user][item] = self._calculateWeights(user, item)
            return self._ratingFromCalculated(*self.calculated[user][item])
        else:
            pass #for now
            #return self._ratingFromCalculated(*self._forceNoCacheRating(user, item))


    def _ratingFromCalculated(self, weightedRatings, sumSimilarities): #done
        """
        Uses the values stored in self.calculated to find the final rating for a user

        Arguments:
            weightedRatings -> The first value in self.calulated it is represented by
                               sum(simil(u, u') * opinions[u'][i] for u' in Users)

            sumSimilarities -> The second value in self.calculated, which represents
                               sum(simil(u, u') for u' in Users)

        Return -> r[u][i], the rating that user u would give to item i
        """

        #forces floating point division
        return float(weightedRatings) / sumSimilarities


    def _calculateWeights(self, user, item): #done
        """
        Calculates the weightedRatings and sum of similarities for a given user based on all of the other users

        Arguments:
            user -> the user for which you are calulating an opinion
            item -> the item that the user does not have an opinion of

        Return -> a tuple (self._ratingTop(user, item), self._ratingBottom(user, item))
        """
        
        #create the users and items sets
        users = {person[0] for person in self.users()} - {user}

        #use those sets to seperately calculate the top and bottom values for the final rating
        return (self._ratingTop(user, item, users), self._ratingBottom(user, item, users)) 


    def _ratingTop(self, user, item, users): #done
        """
        Calculates the top portion of the fraction that a user would have for an item based on other users

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion

        Return -> the top portion of the calculated opinion
        """

        #get the items shared by both users
        return sum(self._similarity(user, other) * self._opinion(other, item) for other in users)


    def _ratingBottom(self, user, item, users): #done
        """
        Calcuates the sum of the similarities between users for a given user/item pair

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion

        Return -> the bottom portion of the rating
        """

        return sum(self._similarity(user, other) for other in users)


    def _similarity(self, user, other): #done
        """
        Calulates the similarity for a given pair of users

        Arguments:
            user  -> the user whose opinion is being calculated
            other -> the other user to whom the user is being compared

        Return -> the similarity between user and other
        """

        if user not in self.similarities:
            self.similarities[user] = {}
        if other not in self.similarities[user]:
            self.similarities[user][other] = self._setSimilarities(user, other)
        return self._calculateSimilarity(*self.similarities[user][other])


    def _calculateSimilarity(self, rssUser, rssOther, multSum): #done
        """
        calculates the similarity between users based on the rss and multSum values

        Arguments:
            rssUser  -> the root sum squared of the ratings of items for the given user
            rssOther -> the root sum squared of the ratings of items for the other used
            multsum  -> the sum of the multiplication of the rating by user and other for an item ie. r{u, i} * r{o, i}

        Return -> the similarity value between two users
        """

        return multSum / (rssUser * rssOther)
        

    def _setSimilarities(self, user, other): #done
        """
        seperately calculate rss(user), rss(other), and multsum(user, other) and return them

        Arguments:
            user  -> a user whose opinion is being predicted
            other -> the user to whom user is being compared

        Return -> tuple(rss(user), rss(other), multsum(user, other))
        """

        items = [column[0] for column in self.items()]
        sharedItems = {item for item in items if self._opinion(user, item) is not 0} & {item for item in items if self._opinion(other, item) is not 0}
        userRss = self._rss(user, sharedItems)
        otherRss = self._rss(other, sharedItems)
        multsum = self._multSum(user, other, sharedItems)
        return (userRss, otherRss, multsum)

        
    def _rss(self, user, shared): #done
        """
        Calulates the root sum squred of the ratings for the given user of the items they share with the other user

        Arguments:
            user   -> a user who has opinions on items
            shared -> the list of items shared with another user to whom they are being compared

        Return -> rss(user) over the shared items with other
        """

        return sqrt(sum(self._opinion(user, item) ** 2 for item in shared))


    def _multSum(self, user, other, shared): #done
        """
        Calulates the sum of the values or r{u, i} * r{o, i} for all shared items

        Arguments:
            user   -> the user whose opinion is being predicted
            other  -> a user to whome user is being compared
            shared -> the set of items shared by the two users

        Return -> the sum of the multiples of the ratings of both users
        """

        return sum(self._opinion(user, item) * self._opinion(other, item) for item in shared)


    def _opinion(self, user, item): #done
        """
        gets the opinion a user has about an item from the database
        
        Arguments:
            user -> a user whose opinion we want
            item -> the item for which we want their opinion

        Return -> the opinion a user has for an item based directly on the database, either a number or 0 representing a null value
        """

        if user not in self.opinions:
            self.opinions[user] = {}
        if item not in self.opinions[user]:
            self.opinions[user][item] = self.fetchOpinion(user, item) or 0
        return self.opinions[user][item]


    def changeOpinion(self, user, item, opinion): #in progress
        """
        Changes a users opinion of an item and psuhes the changes out as necessary

        Arguments:
            user    -> a user whose opinion is changing
            item    -> the item for the user that changes
            opinion -> the new ratings the user has for the item

        Return -> None
        """

        #used to keep track of any changes in the items compared, if an item is removed or added
        items = [column[0] for column in self.items()]
        usersItems = {item for item in items if self._opinion(user, item) is not 0}


        #first, changes the opinion in the database and holds on to the old opinion for use later
        oldOpinion = self.fetchOpinion(user, item)
        self.db.changeOpinion(user, item, opinion)

        #checks to see if the item is removed or not
        change = self._checkNewOrRemoved(user, item, usersItems, opinion, oldOpinion)
        #then this needs to be updated in the opinions matrix
        if user not in self.opinions:
            self.opinions[user] = {}
        self.opinions[user][item] = opinion

        #then this change needs to propgate out to all of the similarities
        users = {person[0] for person in self.users()} - {user}
        for other in users:
            self._updateSimilarities(user, item, other, opinion, change, oldOpinion)


    def _checkNewOrRemoved(self, user, item, items, opinion, oldOpinion):#done
        """
        Checks to see if the item being removed or added

        Arguments:
            user       -> the user whose opinion is being changed
            item       -> the item for which the opinion is changing
            items      -> the list of all items known by that user
            opinion    -> the new opinion

            Return -> -1, 0, or 1.  -1 if the item should be removed from the list, 0 if there are no changes, 
                      and 1 if the item should be added to the list
        """

        if item not in items:
            return 1
        elif item in items and (opinion == 0 or opinion == None):
            return -1
        else:
            return 0


    def _updateSimilarities(self, user, item, other, opinion, change, oldOpinion):#done
        """
        updates the similarity values in the relevant tables

        Arguments:
            user       -> the user whose opinion is being changed
            item       -> the item about which the users opinion changes
            other      -> the other use whose similarity is being compared to
            opinion    -> the new opinion a user has for the item
            change     -> a value -1, 0, or 1, representing whether or not an item needs to be added or removed
                          from the list of items
            oldOpinion -> the old opinion the user had for the item

        Return -> None
        """

        #this whole secion could probably be cleaned up, I'm almost certain it could be in fact
        #maybe refactor it into its own sub-function that gets called twice

        if user in self.similarities:
            #updates the similarities matrix for user
            if other in self.similarities[user]:
                rssUser = sqrt(self.similarities[user][other][0] ** 2 - oldOpinion ** 2 + opinion ** 2)
                newA = self.similarities[user][other][2] + self._opinion(other, item) * (opinion - oldOpinion)
                if change == 1:
                    #adds item to the overall list of items
                    rssOther = sqrt(self.similarities[user][other][1] + self._opinion(other, item) ** 2)
                elif change == -1:
                    #removes item from the overall list of items
                    rssOther = sqrt(self.similarities[user][other][1] - self._opinion(other, item) ** 2)
                else:
                    rssOther = sqrt(self.similarities[user][other][1])
                oldSimil = self._calculateSimilarity(*self.similarities[user][other])
                self.similarities[user][other] = (rssUser, rssOther, newA)
                items = [column[0] for column in self.items()]
                for otherItem in items:
                    self._updateCalculatedRating(user, item, other, opinion, oldOpinion, oldSimil)
            else:
                pass
                #although this could reasonably be set up to instead calculate the ratings instead

        #this should be tested
        if other in self.similarities:
            #updates the similarities matrix for other, in case similarities[other][user] exists
            if user in self.similarities[other]:
                rssUser = sqrt(self.similarities[other][user][0] ** 2 - oldOpinion ** 2 + opinion ** 2)
                newA = self.similarities[other][user][2] + self._opinion(other, item) * (opinion - oldOpinion)
                if change == 1:
                    #adds item to the overall list of items
                    rssOther = sqrt(self.similarities[other][user][1] + self._opinion(other, item) ** 2)
                elif change == -1:
                    #removes item from the overall list of items
                    rssOther = sqrt(self.similarities[other][user][1] - self._opinion(other, item) ** 2)
                else:
                    rssOther = sqrt(self.similarities[other][user][1])
                    #keep in mind that user and other switch in this case,everything else is the same
                oldSimil = self._calculateSimilarity(*self.similarities[other][user])
                self.similarities[other][user] = (rssOther, rssUser, newA)
                items = [column[0] for column in self.items()]
                for otherItem in items:
                    self._updateCalculatedRating(user, item, other, opinion, oldOpinion, oldSimil)
                #then update for the user 
                #self.caculated[user][item] = self._forceNoCacheRating(user, item)
            else:
                pass
                #although once more, this could recalulate everything and set it.


    def _noCacheRating(self, user, item):#done
        """
        Calculates the rating value without using any cached values

        Arguments:
            user -> the user whose rating is being calculated
            item -> the item for which the user is calculating a rating

        Return -> tuple(top, bottom)
        """

        users = {person[0] for person in self.users()} - {user}
        topPart = sum(self._noCacheSimilarity(user, other) * self._opinion(other, item) for other in users)
        bottomPart = sum(self._noCacheSimilarity(user, other) for other in users)
        return (topPart, bottomPart)


    def _noCacheSimilarity(self, user, other): #done
        """
        Calculates the similarity without caching anything directly from the database

        Arguments:
            user  -> the user whose rating is being calculated
            other -> the user to whom they are being compared

        Return -> the similarity value multsum / (rss(u) * rss(u'))
        """

        items = [column[0] for column in self.items()]
        sharedItems = {item for item in items if self._opinion(user, item) is not 0} & {item for item in items if self._opinion(other, item) is not 0}
        multsum = sum(self._noCacheOpinion(user, item) * self._noCacheOpinion(other, item) for item in sharedItems)
        rssUser = sqrt(sum(self._noCacheOpinion(user, item) ** 2 for item in sharedItems))
        rssOther = sqrt(sum(self._noCacheOpinion(other, item) ** 2 for item in sharedItems))
        return multsum / (rssOther * rssUser)


    def _noCacheOpinion(self, user, item):#done
        """
        Gets the opinion from the database, this is quick and easy

        Arguments:
            user -> the user whose rating is being calculated
            item -> the item whose rating is being fetched

        Return ->
        """
        return self.fetchOpinion(user, item) or 0


    def _updateCalculatedRating(self, user, item, other, opinion, oldOpinion, oldSimil):#done
        """
        Updates the calculated ratings matrix for the ratings of all items by a user

        Arguments:
            user       -> the user whose rating is being calculated
            item       -> the item whose rating is being calculated
            other      -> the user to whome they are being compared
            opinion    -> the opinion the user now has for the item
            oldOpinion -> the user's previous opinion for the item
            oldSimil   -> the previous similarity between the two users

        Return -> None
        """

        if other not in self.calculated:
            return
        if item not in self.calculated[other]:
            return
        newTop = self.calculated[other][item][0] + self.similarities[other][other] * opinion - oldOpinion * oldSimil
        newBot = self.calculated[other][item][1] - oldSimil + self.similarities[other][other]
        self.calculated[other][item] = (newTop, newBot)



if __name__ == "__main__":
    assert 1 == 1
    #do more
    x = CollaborativeFilter("database.db", "databases/data", "main")
    users = ["one", "two", "three", "four"]
    classes = ["CS1331", "CS1332", "CS1333", "CS1334"]
    for user in users:
        for clazz in classes:
            assert x._noCacheRating(user, clazz)[0] / x._noCacheRating(user, clazz)[1] == x.predictOpinion(user, clazz)
            stdout.write(user+" "+clazz+" - "+str(x.predictOpinion(user, clazz))+"\n")
