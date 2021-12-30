import sqlite3
import matplotlib.pyplot as plt

import numpy as np
from sklearn.linear_model import LinearRegression


connection1 = sqlite3.connect('mondial.db') # establish database connection
cursor1 = connection1.cursor() # create a database query cursor

def QuestionE():

    createTable()
    #Name, Country, a, b, score
    #Name, Country, Population, Year
    for i in range(1950,2051):
        query = "INSERT INTO Prediction (Name, Country, Population, Year) SELECT Name, Country, a*" + str(i) + "+b," + str(i) + " FROM LinearPrediction;"
        cursor1.execute(query)
        connection1.commit()
    

def createTable():
    
    query = "DROP TABLE IF EXISTS Prediction;"
    cursor1.execute(query)
    connection1.commit()  
        # by default in pgdb, all executed queries for connection 1 up to here form a transaction
        # we can also explicitly start transaction by executing BEGIN TRANSACTION
    
    sql_create_linearprediction = """CREATE TABLE Prediction (
                                        Name TEXT NOT NULL,
                                        Country TEXT NOT NULL,
                                        Population INTEGER NOT NULL,
                                        Year INTEGER NOT NULL,
                                        PRIMARY KEY(Name,Country,Year)
                                    );"""
    cursor1.execute(sql_create_linearprediction)
    connection1.commit()

QuestionE()

cursor1.execute("SELECT Year, SUM(Population) FROM Prediction GROUP BY Year,Name;")
data = cursor1.fetchall()
connection1.commit()

xs = list()
ys = list()
for r in data:
    xs.append(float(r[0]))
    ys.append(float(r[1]))

# print(xs)
plt.scatter(xs, ys,s = 5)
plt.show()
connection1.close()
