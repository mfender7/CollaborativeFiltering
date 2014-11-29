import glob, os
import databases.database as databases
import datetime


#class DataParser(object):

#def __init__(self, folder, db):
#    self.folder = folder
#    self.databaes = db
start = datetime.datetime.now()
databaes = databases.Database("test.db", "sqlite:////Users/mfender/School/PROJECT/CollaborativeFiltering/rawr.db")

#def parse_data(self):
files = []
for x in os.listdir('dataset/training_set/'):
    if not os.path.isfile(x):
        files.append(x)

movies = dict()

for item in files:
    with open('dataset/training_set/'+ item, 'r') as f:
        data = f.readlines()
        mid = 0
        #loop through it all!
        for line in data:
            if ":" in line:
                mid = int(line.split(':')[0])
                movies[mid] = {}
            else:
                d = line.split(',')
                movies[mid][int(d[0])] = int(d[1])
#return movies
#now import it all into the database!
#def import_data(self, data):

counter = 0
with open('import.sql', 'w') as f:
    f.write('PRAGMA synchronous = OFF;')
    f.write('PRAGMA journal_mode = MEMORY;')
    f.write('begin transaction;')
    for key, value in movies.items():
        for k in value:
            if counter <= 1000000:
                f.write('insert into opinions values({}, {}, {});\n'.format(key, k, movies[key][k]))
                print('Movie {} rated by user {} with rating {}'.format(key, k, movies[key][k]))
#            databaes.add_opinion(session, key, k, movies[key][k])
            else:
                count = 0
                f.write('end transaction; begin transaction;\n')

end = datetime.datetime.now()
print('Time to complete: {}'.format((end - start)))
