#!/usr/bin/python

import sqlite3
import matplotlib.pyplot as plt

import numpy as np
from sklearn.linear_model import LinearRegression


connection1 = sqlite3.connect('mondial.db') # establish database connection
cursor1 = connection1.cursor() # create a database query cursor

# This scripts illustrates how you can use output from a query, cast it to python floats,
# and then use a figure plotting library called Matplotlib to create a scatterplot of the
# data.

# Make sure you have installed python as well as sqlite3 python libraries

# documentation of plotting library: https://matplotlib.org/, you can use any other
# library if you like


def query():
    # Here we test some concurrency issues.
    #Question A
    xy = "SELECT Year, Population FROM PopData"

    #Question B
    xy = "SELECT Year, SUM(Population) FROM PopData GROUP BY Year"

    #Question C
    city_in = input("Which city do you want to see?:")
    country_in = input("Which country is the city located?:")
    xy = "SELECT Year, SUM(Population) FROM PopData WHERE Name = '"+city_in+"' AND Country = '"+country_in+"' GROUP BY Year"
    
    #Question D
    # createTable()

    print("U1: (start) "+ xy)
    try:
        cursor1.execute(xy)
        data = cursor1.fetchall()
        print(data)
        connection1.commit()
    except sqlite3.Error as e:
        print( "Error message:", e.args[0])
        connection1.rollback()
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
    return [xs, ys, city_in]

def QuestionD():

    connection2 = sqlite3.connect('mondial.db') # establish database connection
    cursor2 = connection1.cursor() # create a database query cursor 

    createTable()
    cc = "SELECT Name, Country FROM PopData GROUP BY Name, Country LIMIT 50;"
    # for row in cursor1.execute(cc):
    #     print(row)
    
    for row in cursor2.execute(cc):
        # print(row)
        xy = "SELECT Year, SUM(Population) FROM PopData WHERE Name = (?) AND Country = (?) GROUP BY Year"

        # try:
        cursor1.execute(xy,row)
        data_xy = cursor1.fetchall()
        # print(data_xy)
        connection1.commit()
            # except sqlite3.Error as e:
            #     print( "Error message:", e.args[0])
            #     connection1.rollback()
            #     pass
        xs= []
        ys= []
        for r in data_xy:
                # you access ith component of row r with r[i], indexing starts with 0
                # check for null values represented as "None" in python before conversion and drop
                # row whenever NULL occurs
                # print("Considering tuple", r)
            if (r[0]!=None and r[1]!=None):
                xs.append(float(r[0]))
                ys.append(float(r[1]))
            else:
                print("Dropped tuple ", r)
        print(len(xs), len(ys), row)
        score, a,b = linReg(xs, ys)
        if score <=1 and score >= 0:
            values = (row[0], row[1], a, b, score)
            query = """INSERT INTO LinearPrediction VALUES(?,?,?,?,?)"""
            cursor1.execute(query, values)
            connection1.commit()       
    # connection2.commit()
    # connection2.close()

    # except sqlite3.Error as e:
    #     print( "Error message:", e.args[0])
    #     connection1.rollback()
    #     pass

def createTable():
    
    query = "DROP TABLE IF EXISTS Linearprediction"
    cursor1.execute(query)
    connection1.commit()  
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
    cursor1.execute(sql_create_linearprediction)
    connection1.commit()
        
def linReg(xs, ys):
    regr = LinearRegression().fit(np.array(xs).reshape([-1,1]), np.array(ys).reshape([-1,1]))
    score = regr.score(np.array(xs).reshape([-1,1]), np.array(ys).reshape([-1,1]))
    a = regr.coef_[0][0]
    b = regr.intercept_[0]

    return score, a, b

def close():
    connection1.close()



# when calling python filename.py the following functions will be executed:

# [xs, ys, city_in] = query()

# plt.scatter(xs, ys,s = 5)

# #Question C - Regression
# score, a, b = linReg(xs,ys)
# plt.plot(xs,a*np.asarray(xs)+b, "r-")
# #Question A - title
# plt.title("City Population raw data")
# #Question B - title
# plt.title("Total city population by year in database - Erroneous Data!")
# #Question C - title
# plt.title("City Population and prediction for: "+city_in+", a=" +str(a)+",b ="+str(b)+",score ="+ str(score))
# plt.savefig("figure.png") # save figure as image in local directory
# plt.show()  # display figure if you run this code locally, otherwise comment out

#Questioin D
QuestionD()
close()


