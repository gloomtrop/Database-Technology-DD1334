#!/usr/bin/python
import sqlite3
from sys import argv
import matplotlib.pyplot as plt


class Program:
    def __init__(self): #PG-connection setup
        self.conn = sqlite3.connect('mondial.db') # establish database connection
        self.cur = self.conn.cursor() # create a database query cursor

        # specify the command line menu here
        self.actions = [self.population_query, self.exit]
        # menu text for each of the actions above
        self.menu = ["Population Query", "Exit"]
        self.cur = self.conn.cursor()
    def print_menu(self):
        """Prints a menu of all functions this program offers.  Returns the numerical correspondant of the choice made."""
        for i,x in enumerate(self.menu):
            print("%i. %s"%(i+1,x))
        return self.get_int()
    def get_int(self):
        """Retrieves an integer from the user.
        If the user fails to submit an integer, it will reprompt until an integer is submitted."""
        while True:
            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(self.menu):
                    return choice
                print("Invalid choice.")
            except (NameError,ValueError, TypeError,SyntaxError):
                print("That was not a number, genious.... :(")
 
    def population_query(self):
        minpop = input("min_population: ")
        maxpop = input("max_population: ")
        print("minpop: %s, maxpop: %s" % (minpop, maxpop))
        try:
            query ="SELECT * FROM City WHERE population >=%s AND population <= %s" % (minpop, maxpop)
            print("Will execute: ", query)
            result = self.cur.fetchall()
            self.cur.execute(query)
        except sqlite3.Error as e:
            print ("Error message:", e.args[0])
            self.conn.rollback()
            exit()

        self.print_answer(result)

    def exit(self):    
        self.cur.close()
        self.conn.close()
        exit()

    def print_answer(self, result):
        print("-----------------------------------")
        for r in result:
            print(r)
        print("-----------------------------------")

    def run(self):
        while True:
            try:
                self.actions[self.print_menu()-1]()
            except IndexError:
                print("Bad choice")
                continue


# This scripts illustrates how you can use output from a query, cast it to python floats,
# and then use a figure plotting library called Matplotlib to create a scatterplot of the
# data.

# Make sure you have installed python as well as sqlite3 python libraries

# documentation of plotting library: https://matplotlib.org/, you can use any other
# library if you like

def drop():
    # delete the table XYData if it does already exist
    try:
        query = "DROP TABLE XYData"
        cursor1.execute(query)
        connection1.commit()  
        # by default in pgdb, all executed queries for connection 1 up to here form a transaction
        # we can also explicitly start transaction by executing BEGIN TRANSACTION
    except sqlite3.Error as e:
        print("ROLLBACK: XYData table does not exists or other error.")
        print("Error message:", e.args[0])
        connection1.rollback()
        pass

def init():
    try:
        # Create table sales and add initial tuples
        query = "CREATE TABLE XYData(x decimal, y decimal)"
        cursor1.execute(query)
        query = """INSERT INTO XYData VALUES(12.1, 1.00)"""
        cursor1.execute(query)
        query = """INSERT INTO XYData VALUES(16.3, 12.1)"""
        cursor1.execute(query)
        query = """INSERT INTO XYData VALUES(6.3, 22.1)"""
        cursor1.execute(query)
        query = """INSERT INTO XYData VALUES(12.3, 32.1)"""
        cursor1.execute(query)
        query = """INSERT INTO XYData VALUES(NULL, 25.1)"""
        cursor1.execute(query)

        # this commits all executed queries forming a transaction up to this point
        connection1.commit()
    except sqlite3.Error as e:
        print( "Error message:", e.args[0])
        connection1.rollback()

def query():
    # Here we test some concurrency issues.
    xy = "select x, y from XYData"
    print("U1: (start) "+ xy)
    try:
        cursor1.execute(xy)
        data = cursor1.fetchall()
        connection1.commit()
    except sqlite3.Error as e:
        print( "Error message:", e.args[0])
        connection1.rollback()
        exit()

    xs= []
    ys= []
    for r in data:
        # you access ith component of row r with r[i], indexing starts with 0
        # check for null values represented as "None" in python before conversion and drop
        # row whenever NULL occurs
        print("Considering tuple", r)
        if (r[0]!=None and r[0]!=None):
            xs.append(float(r[0]))
            ys.append(float(r[1]))
        else:
            print("Dropped tuple ", r)
    print("xs:", xs)
    print("ys:", ys)
    return [xs, ys]

def close():
    connection1.close()


# when calling python filename.py the following functions will be executed:
drop()
init()
[xs, ys] = query()
plt.scatter(xs, ys)
plt.savefig("figure.png") # save figure as image in local directory
plt.show()  # display figure if you run this code locally, otherwise comment out
close()

if __name__ == "__main__":
    db = Program()
    db.run()
