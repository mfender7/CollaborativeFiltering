"""
extended test cases for the collaorative filter
"""

import CollabFilter as collab
from timeit import timeit
from string import ascii_uppercase
import types
import pprint

letters = ascii_uppercase
names = [a+b for a in letters for b in letters]
classes = ["CS"+ str(i) + str(n) for i in xrange(10) for n in xrange(10)]
test_filter = collab.CollaborativeFilter("test.db", "databases/data", "main")


def fill_database():
    """
    a
    """

    for name in names:
        test_filter.db.addUser(name)

    for class_ in classes:
        test_filter.db.newField(class_)

    counter = 0
    for user in names:
        for course in classes:
            test_filter.db.changeOpinion(user, course, counter)
            #print counter
            counter += 1

    print test_filter.db.currentOpinion("ab", "CS12")


def test_cached(calls, changes, secondary_calls):
    for position in xrange(calls):
        test_filter.predictOpinion(names[position], classes[len(classes) - position - 3])
    for position in xrange(changes):
        test_filter.changeOpinion(names[position], classes[len(classes) - position - 3], position)
    for position in xrange(secondary_calls):
        test_filter.predictOpinion(names[position], classes[len(classes) - position - 3])

def test_no_cache(calls, changes, secondary_calls):
    for position in xrange(calls):
        test_filter._noCacheRating(names[position], classes[len(classes) - position - 3])
    for position in xrange(changes):
        test_filter.changeOpinion(names[position], classes[len(classes) - position - 3], position)
    for position in xrange(secondary_calls):
        test_filter._noCacheRating(names[position], classes[len(classes) - position - 3])

def overall_test(first, second, third, runs=1):
    print "no caching with " + str(runs) + " iterations"
    print timeit("test_no_cache("+str(first)+", "+str(second)+", "+str(third)+")", number=runs, setup="from __main__ import test_no_cache")
    print "caching with " + str(runs) + " iterations"
    print timeit("test_cached("+str(first)+", "+str(second)+", "+str(third)+")", number=runs, setup="from __main__ import test_cached")

def overall_test_with_shenanigans(first, second, third, runs=1):

    methods = [method for method in dir(test_filter) if type(getattr(test_filter, method)) == types.MethodType]
    counter = {getattr(test_filter, method): 0 for method in methods}
    #print methods

    for method in methods:
        def wrapper(function):
            def newFunction(*args, **kwargs):
                #print function
                counter[function] += 1
                return function(*args, **kwargs)
            return newFunction
        setattr(test_filter, method, wrapper(getattr(test_filter, method)))

    test_cached(first, second, third)
    pprint.pprint(counter)

    for item in counter:
        counter[item] = 0


    test_no_cache(first, second, third)
    pprint.pprint(counter)

if __name__ == "__main__":
    #fill_database()
    #overall_test(1, 1, 1)
    overall_test_with_shenanigans(1,1,1)

