from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
import sqlite3

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to connect the database
def db_connect():
    # Connect to the SQLite3 datatabase
    con = sqlite3.connect("meal_planner.db")
    # Use sqlite3.Row to access columns by name
    con.row_factory = sqlite3.Row
    # Create a cursor object
    cur = con.cursor()
    return cur

# close the connection
def db_close(con):
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
        # Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
        # Fetch the results: Use fetchall() to get all results or fetchone() for a single row
        recipe = cur.fetchall()
        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (id,))
        ing_used = cur.fetchall()

        # Close the connection
        db_close(cur)

        # Send the results of the SELECT to the list.html page
        return render_template("recipe.html", recipe=recipe, ing_used=ing_used)

        
    else:
        # Connect to the database and create a cursor
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT id, name FROM recipes")
        # Fetch the results: use fetchall() to get all results or fetchone() for a single row
        rows = cur.fetchall()
        # Close the connection
        db_close(cur)

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

        # Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
        recipe = cur.fetchall()

        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (id,))
        ing_used = cur.fetchall()

        # Close the connection
        db_close(cur)

        # Send the results of the SELECT to the list.html page
        return render_template("recipe.html", recipe=recipe, ing_used=ing_used)
       
               
    else:   
        query = request.args.get("query")
        if query:
            # Connect to the SQLite3 datatabase
            cur = db_connect()
            # Step 4: Execute the SELECT query
            cur.execute("SELECT id, name FROM recipes WHERE name LIKE ? LIMIT 50", (query,))
            # Step 5: Fetch the results
            # Use fetchall() to get all results or fetchone() for a single row
            recipes = cur.fetchall()
            # Close the connection
            db_close(cur)
            
        else:
            recipes = []
        return render_template("search.html", recipes=recipes)
    
# Route to form used to edit recipe and save to the database the revised recipe
@app.route("/edit_recipe", methods=["GET", "POST"])
def edit_recipe():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        recipe_id = request.form.get("recipe_id")

        recipe_name = request.form.get("recipe_name")
        if not recipe_name:
            return render_template('result.html', msg = "Please complete a recipe name")
        
        instructions = request.form.get("recipe_instructions")
        if not instructions:
            return render_template('result.html', msg = "Please complete instructions for the recipe")

        try:
            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE recipes SET name = ?, instructions = ? WHERE id = ?", (recipe_name, instructions, recipe_id))

                con.commit()
                msg = "Record successfully edited in the database"
        except:
            con.rollback()
            msg = "Error in the Edit"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html', msg=msg) 

    else:
        id = request.args.get("id")

        # Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
        recipe = cur.fetchall()

        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (id,))
        ing_used = cur.fetchall()

        # Close the connection
        db_close(cur)


        return render_template("edit_recipe.html", recipe=recipe, ing_used=ing_used)

# Route to form used to delete a recipe
@app.route("/delete_recipe", methods=["GET", "POST"])
def delete_recipe():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        recipe_id = request.form.get("recipe_id")

        recipe_name = request.form.get("recipe_name")
        if not recipe_name:
            return render_template('result.html', msg = "Please complete a recipe name")
        
        instructions = request.form.get("recipe_instructions")
        if not instructions:
            return render_template('result.html', msg = "Please complete instructions for the recipe")

        try:
            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE recipes SET name = ?, instructions = ? WHERE id = ?", (recipe_name, instructions, recipe_id))

                con.commit()
                msg = "Record successfully edited in the database"
        except:
            con.rollback()
            msg = "Error in the Edit"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html', msg=msg) 

    else:
        id = request.args.get("id")

        # Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
        recipe = cur.fetchall()

        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (id,))
        ing_used = cur.fetchall()

        # Close the connection
        db_close(cur)

        return render_template("delete_recipe.html", recipe=recipe, ing_used=ing_used)