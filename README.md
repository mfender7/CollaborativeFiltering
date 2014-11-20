[![PDF Status](https://www.sharelatex.com/github/repos/joshuamorton/ClassRank/builds/latest/badge.svg)](https://www.sharelatex.com/github/repos/joshuamorton/ClassRank/builds/latest/output.pdf)

ClassRank
=========

(name up for reconsideration)

A webapp that uses Collaborative Filtering to help people figure out what (specifically Georgia Tech Computer Science) classes they should take because they will be able to handle them and enjoy them.  

##Setup

(inside the environment of your choice)

1. Install Python3 (`sudo apt-get install python3`)
2. Install the Tornado webserver (`pip3 install tornado`)
3. Install the scrypt hashing library (`pip3 install scrypt`)
4. Change `cookie_secret` (routing.py line 28) to something actually secure
5. From the main directory (where routing.py is) add the first school to the database with `python3 routing.py add_school "[school name]" "[school abbreviation]"` (it might be wise to make this a fake school such as "Test university" or "Admin Community College" or something similarly apt)
6. `python3 routing.py runserver`
7. Set the port (default 8888)
8. Navigate to "localhost:[port]/register"
9. Fill out the form and click "Register Now!"
10. Back to the command line, end the event loop (Ctrl+C) and run `python3 routing.py admin [username]` where [username] is the name you just registered with
11. python3 routing.py runserver`
12. Navigate to "localhost:[port]/admin"
13. Log in with your credentials make use of the much better admin panel via web interface
14. Log out
15. Navigate to "localhost:[port]/login"
16. Log in and see what normal users see
17. Rejoice
