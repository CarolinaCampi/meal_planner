from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
import sqlite3

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to perform SELECT queries on the database
def db_select(query):
    # Connect to the SQLite3 datatabase
    con = sqlite3.connect("meal_planner.db")
    # Use sqlite3.Row to access columns by name
    con.row_factory = sqlite3.Row
    # Create a cursor object
    cur = con.cursor()
    # Execute the SELECT query
    cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
    # Fetch the results
    # Use fetchall() to get all results or fetchone() for a single row
    recipe = cur.fetchall()
    # Execute the second SELECT query on 'ing_used' table
    cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (id,))
    ing_used = cur.fetchall()

    # Step 7: Close the connection
    con.close()

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
        # SELECT all columns of the row with the matching id in the recipe table.
        con = sqlite3.connect("meal_planner.db")
        # Use sqlite3.Row to access columns by name
        con.row_factory = sqlite3.Row
        # Create a cursor object
        cur = con.cursor()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
        # Fetch the results
        # Use fetchall() to get all results or fetchone() for a single row
        recipe = cur.fetchall()
        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (id,))
        ing_used = cur.fetchall()

        # Step 7: Close the connection
        con.close()

        # Send the results of the SELECT to the list.html page
        return render_template("recipe.html", recipe=recipe, ing_used=ing_used)

        
    else:
        # Connect to the SQLite3 datatabase and SELECT id and name from the recipes table.
        # Step 1: Connect to the meal_planner.db database
        con = sqlite3.connect("meal_planner.db")
        # Step 2: Use sqlite3.Row to access columns by name
        con.row_factory = sqlite3.Row
        # Step 3: Create a cursor object
        cur = con.cursor()
        # Step 4: Execute the SELECT query
        cur.execute("SELECT id, name FROM recipes")
        # Step 5: Fetch the results
        # Use fetchall() to get all results or fetchone() for a single row
        rows = cur.fetchall()
        # Step 7: Close the connection
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
            return render_template('result.html', msg = "Please complete a recipe name")
        
        instructions = request.form.get("recipe_instructions")
        if not instructions:
            return render_template('result.html', msg = "Please complete instructions for the recipe")

        try:
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO recipes (name, instructions) VALUES (?,?)", (name, instructions,))

                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template("result.html", msg=msg)
               
    else:    
        return render_template("new_recipe.html")


# Route to form used to add a new recipe to the database
@app.route("/search", methods=["GET", "POST"])
def search():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
       # Access form data
        id = request.form.get("id")

        # Connect to the SQLite3 datatabase and 
        # SELECT all columns of the row with the matching id in the recipe table.
        con = sqlite3.connect("meal_planner.db")
        # Use sqlite3.Row to access columns by name
        con.row_factory = sqlite3.Row
        # Create a cursor object
        cur = con.cursor()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
        # Fetch the results
        # Use fetchall() to get all results or fetchone() for a single row
        recipe = cur.fetchall()
        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (id,))
        ing_used = cur.fetchall()

        # Step 7: Close the connection
        con.close()

        # Send the results of the SELECT to the list.html page
        return render_template("recipe.html", recipe=recipe, ing_used=ing_used)
       
               
    else:   
        query = request.args.get("query")
        if query:
            # Connect to the SQLite3 datatabase and SELECT id and name from the recipes table.
            # Step 1: Connect to the meal_planner.db database
            con = sqlite3.connect("meal_planner.db")
            # Step 2: Use sqlite3.Row to access columns by name
            con.row_factory = sqlite3.Row
            # Step 3: Create a cursor object
            cur = con.cursor()
            # Step 4: Execute the SELECT query
            cur.execute("SELECT id, name FROM recipes WHERE name LIKE ? LIMIT 50", (query,))
            # Step 5: Fetch the results
            # Use fetchall() to get all results or fetchone() for a single row
            recipes = cur.fetchall()
            # Step 7: Close the connection
            con.close()
            
        else:
            recipes = []
        return render_template("search.html", recipes=recipes)
