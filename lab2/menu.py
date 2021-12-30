#!/usr/bin/python
import sqlite3
from sys import argv

import matplotlib.pyplot as plt

import numpy as np
from sklearn.linear_model import LinearRegression


class Program:
    def __init__(self): #PG-connection setup
        self.conn = sqlite3.connect('mondial.db') # establish database connection
        self.cur = self.conn.cursor() # create a database query cursor
        # specify the command line menu here
        self.actions = [self.population_query, self.question_a, self.question_b,self.question_c,self.question_d,self.question_e,self.question_f,self.question_g,self.exit]
        # menu text for each of the actions above
        self.menu = ["Population Query", "Question A","Question B","Question C","Question D","Question E", "Question F","Question G","Exit"]
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

    def question_a(self):
        xy = "SELECT Year, Population FROM PopData"
        xs, ys = self.xy_datafetch(xy)
        plt.title("City Population raw data")
        plt.scatter(xs, ys,s = 5)
        plt.show()
        
    def question_b(self):
        xy = "SELECT Year, SUM(Population) FROM PopData GROUP BY Year"
        xs, ys = self.xy_datafetch(xy)
        plt.title("City Population raw data")
        plt.scatter(xs, ys,s = 10)
        plt.show()

    def question_c(self):
        city_in = input("Which city do you want to see?:")
        country_in = input("Which country is the city located?:")
        xy = "SELECT Year, SUM(Population) FROM PopData WHERE Name = '"+city_in+"' AND Country = '"+country_in+"' GROUP BY Year"

        xs, ys = self.xy_datafetch(xy)

        score, a, b = self.linReg(xs,ys)
        plt.plot(xs,a*np.asarray(xs)+b, "r-")
        plt.scatter(xs, ys,s = 5)
        plt.title("City Population and prediction for: "+city_in+", a=" +str(a)+",b ="+str(b)+",score ="+ str(score))
        plt.show()

    def question_d(self): 

        self.createTable_linpred()
        cc = "SELECT Name, Country FROM PopData GROUP BY Name, Country;"
        cur2 = self.conn.cursor()
        
        for row in cur2.execute(cc):
            xy = "SELECT Year, SUM(Population) FROM PopData WHERE Name = (?) AND Country = (?) GROUP BY Year"

            try:
                self.cur.execute(xy,row)
                data_xy = self.cur.fetchall()
                self.conn.commit()
            except sqlite3.Error as e:
                print( "Error message:", e.args[0])
                self.conn.rollback()
                pass
            xs= []
            ys= []
            for r in data_xy:
                if (r[0]!=None and r[1]!=None):
                    xs.append(float(r[0]))
                    ys.append(float(r[1]))
                else:
                    print("Dropped tuple ", r)
            
            # print(xs, ys)
            if len(xs) > 1 and len(ys)> 1:
                score, a,b = self.linReg(xs, ys)

                if score <=1 and score >= 0:
                    values = (row[0], row[1], a, b, score)
                    query = """INSERT INTO LinearPrediction VALUES(?,?,?,?,?)"""
                    self.cur.execute(query, values)
                self.conn.commit()       

    def question_e(self):
        
        self.createTable_pred()

        for i in range(1950,2051):
            query = "INSERT INTO Prediction (Name, Country, Population, Year) SELECT Name, Country, a*" + str(i) + "+b," + str(i) + " FROM LinearPrediction;"
            self.cur.execute(query)
            self.conn.commit()
        
    def question_f(self):
        self.cur.execute("SELECT Year, SUM(Population) FROM Prediction GROUP BY Year,Name;")
        data = self.cur.fetchall()
        self.conn.commit()

        xs = list()
        ys = list()
        for r in data:
            xs.append(float(r[0]))
            ys.append(float(r[1]))

        # print(xs)
        plt.scatter(xs, ys,s = 5)
        plt.title("Regressed Population of each City from 1950-2050")
        plt.show()
    
    def question_g(self):
        false = False
        print("Hypothesis is that industry value per GDP indicate population variation")
        while not false:
            try:
                user_in = int(input("Growing (press '1') or Declining (press '2') or Exit (press '3'): "))
    
                if user_in == 1:
                    false = True
                    self.cur.execute("SELECT Name FROM LinearPrediction WHERE a>0;")
                elif user_in == 2:
                    false = True
                    self.cur.execute("SELECT Name FROM LinearPrediction WHERE a<0;")
                elif user_in == 3:
                    break
                else:
                    print("Not a valid number")
            except:
                print("That was not a number! Try again")
            
        if user_in in (1,2):
            cities = self.cur.fetchall()
            self.conn.commit()
            for city in cities:
                xy = "SELECT Year, Industry FROM PopData WHERE Name = (?) GROUP BY Year"

                self.cur.execute(xy,city)
                data_xy = self.cur.fetchall()
                self.conn.commit()
                        
                xs= []
                ys= []
                for r in data_xy:
                    if (r[0]!=None and r[1]!=None):
                        xs.append(float(r[0]))
                        ys.append(float(r[1]))
                    else:
                        print("Dropped tuple ", r)

                plt.scatter(xs, ys)
            plt.savefig("figure.png")
            plt.show()

            self.question_g()

    def exit(self):    
        self.cur.close()
        self.conn.close()
        exit()

    def xy_datafetch(self, xy):
        try:
            self.cur.execute(xy)
            data = self.cur.fetchall()
            self.conn.commit()
        except sqlite3.Error as e:
            print( "Error message:", e.args[0])
            self.conn.rollback()
            pass

        xs= []
        ys= []
        for r in data:
            # you access ith component of row r with r[i], indexing starts with 0
            # check for null values represented as "None" in python before conversion and drop
            # row whenever NULL occurs
            # print("Considering tuple", r)
            if (r[0]!=None and r[1]!=None):
                xs.append(float(r[0]))
                ys.append(float(r[1]))
            else:
                print("Dropped tuple ", r)
        # print("xs:", xs)
        # print("ys:", ys)
        return xs, ys

    def linReg(self, xs, ys):
        regr = LinearRegression().fit(np.array(xs).reshape([-1,1]), np.array(ys).reshape([-1,1]))
        score = regr.score(np.array(xs).reshape([-1,1]), np.array(ys).reshape([-1,1]))
        a = regr.coef_[0][0]
        b = regr.intercept_[0]

        return score, a, b

    def createTable_linpred(self):
    
        query = "DROP TABLE IF EXISTS LinearPrediction"
        self.cur.execute(query)
        self.conn.commit()  
            # by default in pgdb, all executed queries for connection 1 up to here form a transaction
            # we can also explicitly start transaction by executing BEGIN TRANSACTION
        
        sql_create_linearprediction = """CREATE TABLE LinearPrediction (
                                            Name TEXT NOT NULL,
                                            Country TEXT NOT NULL,
                                            a REAL NOT NULL,
                                            b REAL NOT NULL,
                                            score REAL NOT NULL,
                                            PRIMARY KEY(Name,Country)
                                        );"""
        self.cur.execute(sql_create_linearprediction)
        self.conn.commit()

    def createTable_pred(self):
    
        query = "DROP TABLE IF EXISTS Prediction;"
        self.cur.execute(query)
        self.conn.commit()  
            # by default in pgdb, all executed queries for connection 1 up to here form a transaction
            # we can also explicitly start transaction by executing BEGIN TRANSACTION
        
        sql_create_linearprediction = """CREATE TABLE Prediction (
                                            Name TEXT NOT NULL,
                                            Country TEXT NOT NULL,
                                            Population INTEGER NOT NULL,
                                            Year INTEGER NOT NULL,
                                            PRIMARY KEY(Name,Country,Year)
                                        );"""
        self.cur.execute(sql_create_linearprediction)
        self.conn.commit()

    def plot_answer(self, xs, ys):
        pass

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

if __name__ == "__main__":
    db = Program()
    db.run()
