# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Source: https://github.com/ISM6225/python-flask-sqlite/blob/main/create_table.py
# Description: This python script assumes that you already have
# a database.db file at the root of your workspace.
# This python script will CREATE a table called students 
# in the database.db using SQLite3 which will be used
# to store the data collected by the forms in this app
# Execute this python script before testing or editing this app code. 
# Open a python terminal and execute this script:
# python create_table.py

import sqlite3

con = sqlite3.connect('meal_planner.db')
print("Connected to database successfully")

cur = con.cursor()

result = cur.execute("INSERT INTO ingredients (name) VALUES ('atún'), ('harina'), ('huevos'), ('espinaca'), ('aceite'), ('cebolla')")
print(result)
print("Added data to ingredients successfully")

cur.execute("INSERT INTO units (name) VALUES ('kg'), ('g'), ('lata'), ('unidad'), ('taza'), ('cucharadita')")
print("Added data to units successfully")

con.commit()

con.close()