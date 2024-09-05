from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
import sqlite3

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# From CS50's Finance practice
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/', methods=["GET", "POST"])
def index():
    #User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Access form data
        id = request.form.get("id")

        # Connect to the SQLite3 datatabase and 
        # SELECT rowid and all Rows from the students table.
        con = sqlite3.connect("meal_planner.db")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM recipes WHERE id = " + id)

        row = cur.fetchall()

        con.close()

        # Send the results of the SELECT to the list.html page
        return render_template("recipe.html", row=row)

        
    else:
        # Connect to the SQLite3 datatabase and 
        # SELECT rowid and all Rows from the students table.
        con = sqlite3.connect("meal_planner.db")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT id, name FROM recipes")

        rows = cur.fetchall()

        con.close()
        # Send the results of the SELECT to the list.html page
        return render_template("index.html", rows=rows)


# Route to form used to add a new recipe to the database
@app.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Access form data
        name = request.form.get("recipe_name")
        if not name:
            return render_template('result.html', msg="Please complete a recipe name")
        
        instructions = request.form.get("recipe_instructions")
        if not instructions:
            return render_template('result.html', msg="Please complete instructions for the recipe")

        try:
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO recipes (name, instructions) VALUES (?,?)", (name, instructions))

                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)
               
    else:    
        return render_template("new_recipe.html")

