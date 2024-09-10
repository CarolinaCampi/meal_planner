from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
import sqlite3
import random

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

# Homepage shows a list of the recipes on the database
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
# FALTA AGREGAR HANDLING DE INGREDINTES Y UNIDADES
@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Access form data
        name = request.form.get("recipe_name")
        if not name:
            return render_template('result.html', msg = "Please complete a recipe name")
        
        instructions = request.form.get("recipe_instructions")
        if not instructions:
            return render_template('result.html', msg = "Please complete instructions for the recipe")

        quantity_1 = request.form.get("quantity_1")
        if not quantity_1:
            return render_template('result.html', msg = "Please complete an ingredient quantity")
        
        unit_1 = request.form.get("unit_1")
        if not unit_1:
            return render_template('result.html', msg = "Please complete a unit for the ingredient")
        
        ingredient_1 = request.form.get("ingredient_1")
        if not ingredient_1:
            return render_template('result.html', msg = "Please complete an ingredient for the recipe")

        try:
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO recipes (name, instructions) VALUES (?,?) RETURNING id", (name, instructions,))
                # get the returning id from the inserted row
                row = cur.fetchone()
                (inserted_id, ) = row if row else None

                cur.execute("INSERT INTO ing_used (recipe_id, ing_id, quantity, unit_id) VALUES (?,?,?,?)", (inserted_id, ingredient_1, quantity_1, unit_1))

                con.commit()
                msg = "Record successfully added to database"
        
        except Exception as e:
            # Rollback in case of error
            con.rollback()
            msg = "Error in the INSERT: " + str(e)

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template("result.html", msg=msg)
               
    else:    
        cur = db_connect()
        cur.execute("SELECT * FROM ingredients")
        ingredients = cur.fetchall()

        cur.execute("SELECT * FROM units")
        units = cur.fetchall()

        db_close(cur)
        return render_template("create_recipe.html", ingredients=ingredients, units=units)


# Route to search recipes in the database
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
            cur.execute("SELECT id, name FROM recipes WHERE name LIKE ? LIMIT 50", ("%" + query + "%", ))
            # Step 5: Fetch the results
            # Use fetchall() to get all results or fetchone() for a single row
            recipes = cur.fetchall()
            # Close the connection
            db_close(cur)
            
        else:
            recipes = []
        return render_template("search.html", recipes=recipes)
    
# Route to form used to edit recipe and save to the database the revised recipe
# FALTA AGREGAR LA PARTE DE EDITAR LOS INGREDIENTES
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
        
        except Exception as e:
            # Rollback in case of error
            con.rollback()
            msg = "Error in the UPDATE: " + str(e)

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html', msg=msg) 

    else:
        recipe_id = request.args.get("recipe_id")

        # Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        recipe = cur.fetchall()

        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT * FROM ing_used WHERE recipe_id = ?", (recipe_id,))
        ing_used = cur.fetchall()

        # Close the connection
        db_close(cur)


        return render_template("edit_recipe.html", recipe=recipe, ing_used=ing_used)

# Route to form used to delete a recipe
@app.route("/delete_recipe", methods=["GET", "POST"])
def delete_recipe():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        try:
            # Use the hidden input value of id from the form to get the rowid
            recipe_id = request.form['recipe_id']
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('meal_planner.db') as con:
                    cur = con.cursor()
                    # Delete from 'ing_used' table first to maintain referential integrity
                    cur.execute("DELETE FROM ing_used WHERE recipe_id = ?", (recipe_id,))

                    cur.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
                    # Commit the transaction
                    con.commit()
                    msg = "Records successfully deleted from the database"

        except Exception as e:
            # Rollback in case of error
            con.rollback()
            msg = "Error in the DELETE: " + str(e)

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

    else:
        recipe_id = request.args.get("recipe_id")

        # Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        recipe = cur.fetchall()

        # Close the connection
        db_close(cur)

        return render_template("delete_recipe.html", recipe=recipe)
    

# Route to access the meal planner functionality
@app.route("/create_plan", methods=["GET", "POST"])
def create_plan():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        meal_number = request.form.get("meal_number")
        if not (meal_number):
            return render_template("result.html", msg="Please insert a number of meals.")
        try:
            meal_number = int(meal_number)
        except ValueError:
            return render_template("result.html", msg="Please insert a valid number of meals.")
        if meal_number < 1:
            return render_template("result.html", msg="Please insert a number of meals greater than zero.")

        # Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT COUNT(*) FROM recipes")
        recipes_number = cur.fetchall()
        
        recipes_number = recipes_number[0]["COUNT(*)"]

        if meal_number > recipes_number:
            msg = "The number pf meals requested is greater than the recipes in the database, " + recipes_number
            return render_template("result.html", msg=msg)

        unique_ids = random.sample(range(0, recipes_number), meal_number)
        print(unique_ids)

        placeholders = ','.join('?' for _ in unique_ids)
        query = f"SELECT * FROM recipes WHERE id IN ({placeholders})"

        cur.execute(query, unique_ids)

        recipes = cur.fetchall()

        # Close the connection
        db_close(cur)

        return render_template("create_plan.html", recipes=recipes)


    else:
        return render_template("create_plan.html")
    



