import glob, os
import databases.database as databases

#grab all files first...
files = []
for x in os.listdir('dataset/training_set'):
    if not os.path.isfile(x):
        files.append(x)

movies = dict()

for item in files:
    with open('dataset/training_set/' + item, 'r') as f:
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

#now import it all into the database!
