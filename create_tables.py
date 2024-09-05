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

conn = sqlite3.connect('meal_planner.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE recipes (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, instructions TEXT NOT NULL)')
print("Created recipes table successfully!")

conn.execute('CREATE TABLE ingredients (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL)')
print("Created ingredients table successfully!")

conn.execute('CREATE TABLE units (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL)')
print("Created units table successfully!")

conn.execute('CREATE TABLE ing_used (recipe_id INTEGER NOT NULL, ing_id INTEGER NOT NULL, quantity FLOAT NOT NULL, unit_id INTEGER NOT NULL, FOREIGN KEY (recipe_id) REFERENCES recipes(id), FOREIGN KEY (ing_id) REFERENCES ingredients(id), FOREIGN KEY (unit_id) REFERENCES units(id))')
print("Created ing_used table successfully!")

conn.close()