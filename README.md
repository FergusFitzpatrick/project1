# Project 1

Web Programming with Python and JavaScript

When the app is opened, you are brought to the index.html page, this is the only time you see the index.html page. It directs the user to either log in or sign up.
Once the user clicks a link the brand name in the navbar, it directs the user to the search page but only if the users has been logged in. If the user is not logged in, the user will be brought to the log in page.

The login_required.py file wraps a function f around a conditional statement of weather a user is logged in or not. This is done by checking if the session variable username is None.

The books.csv file is just the given file to import the books information.

import.py contains the "INSERT" commands to import the csv file into the books table in the psql database.
