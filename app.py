from flask import Flask, flash, jsonify, redirect, render_template, request, session, g
# from flask_session import Session
import sqlite3

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

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
        cur.execute("SELECT ing_used.quantity, ingredients.name AS ing_name, units.name AS unit_name FROM ing_used JOIN ingredients ON ingredients.id = ing_used.ing_id JOIN units ON units.id = ing_used.unit_id WHERE ing_used.recipe_id = ?", (id,))
        ing_used = cur.fetchall()
        
        # Close the connection
        db_close(cur)

        # Send the results of the SELECT to the list.html page
        return render_template("recipe.html", recipe=recipe, ing_used=ing_used)

    else:
        # Connect to the database and create a cursor
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT id, name FROM recipes ORDER BY name ASC")
        # Fetch the results: use fetchall() to get all results or fetchone() for a single row
        rows = cur.fetchall()
        # Close the connection
        db_close(cur)

        # Send the results of the SELECT to the list.html page
        return render_template("index.html", rows=rows)


# Route to form used to add a new recipe to the database
# FALTA AGREGAR HANDLING DE NUEVOS INGREDINTES Y UNIDADES
@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Access form data
        result = request.form

        name = request.form.get("recipe_name")
        if not name:
            return render_template('result.html', msg = "Please complete a recipe name")
        name = name.capitalize()

        instructions = request.form.get("recipe_instructions")
        if not instructions:
            return render_template('result.html', msg = "Please complete instructions for the recipe")

        try:
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO recipes (name, instructions) VALUES (?,?) RETURNING id", (name, instructions,))
                # get the returning id from the inserted row
                row = cur.fetchone()
                (inserted_id, ) = row if row else None

                query_values = {}
                for key, value in result.items():
                    if key != "recipe_name" and key != "recipe_instructions":
                        number = key.split("_")[1]
                        category = key.split("_")[0]

                        if number not in query_values:
                            query_values[number] = [inserted_id, None, None, None]

                        if category == "ingredient":
                            query_values[number][1] = value

                        if category == "quantity":
                            query_values[number][2] = value
                        
                        if category == "unit":
                            query_values[number][3] = value
                
                for row in query_values.values():
                    cur.execute("INSERT INTO ing_used (recipe_id, ing_id, quantity, unit_id) VALUES (?,?,?,?)", tuple(row))

                con.commit()
                msg = "Record successfully added to database"
        
        except Exception as e:
            # Rollback in case of error
            con.rollback()
            print(e)
            msg = "Error in the INSERT: " + str(e)

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template("result.html", msg=msg)
               
    else:    
        cur = db_connect()
        cur.execute("SELECT * FROM ingredients ORDER BY name ASC")
        ingredients = cur.fetchall()

        cur.execute("SELECT * FROM units ORDER BY name ASC")
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
        cur.execute("SELECT ing_used.quantity, ingredients.name AS ing_name, units.name AS unit_name FROM ing_used JOIN ingredients ON ingredients.id = ing_used.ing_id JOIN units ON units.id = ing_used.unit_id WHERE ing_used.recipe_id = ?", (id,))
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
            cur.execute("SELECT id, name FROM recipes WHERE name LIKE ? ORDER BY name ASC LIMIT 50", ("%" + query + "%", ))
            # Step 5: Fetch the results
            # Use fetchall() to get all results or fetchone() for a single row
            recipes = cur.fetchall()
            # Close the connection
            db_close(cur)
            
        else:
            recipes = []
        return render_template("search.html", recipes=recipes)

# Function that displays the edit menu for a recipe with id = recipe_ip
def display_edit_recipe(edited_recipe_id):
# Connect to the SQLite3 datatabase
        cur = db_connect()
        # Execute the SELECT query
        cur.execute("SELECT * FROM recipes WHERE id = ?", (edited_recipe_id,))
        recipe = cur.fetchall()

        cur.execute("SELECT * FROM ingredients ORDER BY name ASC")
        all_ingredients = cur.fetchall()

        cur.execute("SELECT * FROM units ORDER BY name ASC")
        all_units = cur.fetchall()

        # Execute the second SELECT query on 'ing_used' table
        cur.execute("SELECT ing_used.quantity, ingredients.name AS ing_name, ingredients.id AS ing_id, units.name AS unit_name, units.id AS unit_id FROM ing_used JOIN ingredients ON ingredients.id = ing_used.ing_id JOIN units ON units.id = ing_used.unit_id WHERE ing_used.recipe_id = ?", (edited_recipe_id,))
        ing_used = cur.fetchall()

        # Close the connection
        db_close(cur)

        return render_template("edit_recipe.html", recipe=recipe, ing_used=ing_used, all_ingredients=all_ingredients, all_units=all_units)

# Route to form used to edit recipe and save to the database the revised recipe
# FALTA AGREGAR NUEVOS INGREDIENTES O UNIDADES (IDEM CREATE_RECIPE)
@app.route("/edit_recipe", methods=["GET", "POST"])
def edit_recipe():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        result = request.form
        recipe_id = request.form.get("recipe_id")

        recipe_name = request.form.get("recipe_name")
        if not recipe_name:
            return render_template('result.html', msg = "Please complete a recipe name")
        
        recipe_name = recipe_name.capitalize()

        instructions = request.form.get("recipe_instructions")
        if not instructions:
            return render_template('result.html', msg = "Please complete instructions for the recipe")

        try:
            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE recipes SET name = ?, instructions = ? WHERE id = ?", (recipe_name, instructions, recipe_id))
                # Delete exiting ingredients
                cur.execute("DELETE FROM ing_used WHERE recipe_id = ?", (recipe_id,))
                # Insert new ingredients
                query_values = {}
                for input_name, input_value in result.items():
                    if input_name != "recipe_name" and input_name != "recipe_instructions" and input_name != "recipe_id":
                        number = input_name.split("_")[1]
                        category = input_name.split("_")[0]

                        if number not in query_values:
                            query_values[number] = [recipe_id, None, None, None]

                        if category == "ingredient":
                            query_values[number][1] = input_value

                        if category == "quantity":
                            query_values[number][2] = input_value
                        
                        if category == "unit":
                            query_values[number][3] = input_value
                
                for row in query_values.values():
                    cur.execute("INSERT INTO ing_used (recipe_id, ing_id, quantity, unit_id) VALUES (?,?,?,?)", tuple(row))
                
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

        return display_edit_recipe(recipe_id)

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
# Add export and shopping list capabilities: tal vez que se pueda copiar imprimir a pantalla y copiar?
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
        cur.execute("SELECT * FROM recipes ORDER BY random() LIMIT ?", (meal_number,))
        recipes = cur.fetchall()

        # Close the connection
        db_close(cur)

        # Process recipes to get the id?

        return render_template("create_plan.html", recipes=recipes)
    else:
        return render_template("create_plan.html")
    
# See shopping list and copy to clipboard
@app.route("/shopping_list", methods=["POST"])
def shopping_list():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        recipes_id = request.form
        print(recipes_id)

        query_ids = []
        for input_name, input_value in recipes_id.items():
            category = input_name.split("_")[0]

            if category == "id":
                query_ids.append(input_value)

        print(query_ids)
        # Connect to the SQLite3 datatabase
        cur = db_connect()

        placeholders = ','.join('?' for _ in query_ids)
        # Recipes query
        recipes_query = f"SELECT * FROM recipes WHERE id IN ({placeholders})"
        # Execute the SELECT query
        cur.execute(recipes_query, query_ids)
        
        recipes = cur.fetchall()

        # Ingredients used query
        ing_used_query = f"SELECT SUM(ing_used.quantity) AS quantity, ingredients.name AS ing_name, units.name AS unit_name FROM ing_used JOIN ingredients ON ingredients.id = ing_used.ing_id JOIN units ON units.id = ing_used.unit_id WHERE ing_used.recipe_id IN ({placeholders}) GROUP BY ing_used.ing_id"
        # Execute the SELECT query
        cur.execute(ing_used_query, query_ids)
        
        ing_used = cur.fetchall()

        # Close the connection
        db_close(cur)

        return render_template("shopping_list.html", recipes=recipes, ing_used=ing_used)
    
# Create new unit
# REVISAR CUANDO ESTAMOS EN EDIT_RECIPE
@app.route("/create_unit", methods=["POST"])
def create_unit():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        new_unit = request.form.get("new_unit")

        if not new_unit:
            return render_template("result.html", msg="Please input a valid ingredient.")
        
        new_unit = new_unit.lower()

        try:
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO units (name) VALUES (?)", (new_unit,))
                con.commit()
                # msg = "Record successfully edited in the database"
        
        except Exception as e:
            # Rollback in case of error
            con.rollback()
            # msg = "Error in the UPDATE: " + str(e)
            print(e)

        finally:
            con.close()
            # Send the transaction message to result.html
        
        # check if the request came from create_recipe or edit_recipe
        # Only edit_recipe passes the recipe_id
        recipe_id = request.form.get("recipe_id")
        if not recipe_id:
            print("not recipe id")
            # Redirect to create recipe to start again the creation
            return redirect('create_recipe') 
        else:
            print("else")
            print(recipe_id)
            return display_edit_recipe(recipe_id)


# Create new ingredient
@app.route("/create_ingredient", methods=["POST"])
def create_ingredient():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        request_data = request.get_json()
        
        new_ing = request_data["new_ing"]

        if not new_ing:
            return render_template("result.html", msg="Please input a valid ingredient.")

        new_ing = new_ing.lower()

        try:
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO ingredients (name) VALUES (?) RETURNING id", (new_ing,))
                # get the returning id from the inserted row
                row = cur.fetchone()
                (inserted_id, ) = row if row else None

                con.commit()
                # msg = "Record successfully edited in the database"
        
        except Exception as e:
            # Rollback in case of error
            con.rollback()
            # msg = "Error in the UPDATE: " + str(e)
            print(e)

        finally:
            con.close()
        
        # Check if the request came from create_recipe or edit_recipe
        # Only edit_recipe passes the recipe_id        
        if "recipe_id" not in request_data:
            print("No recipe id so the request came from create_recipe")
            # Redirect to create recipe to start again the creation
            # return redirect('create_recipe') 

            # Return the new option as a JSON response
            return jsonify({"ing_id": inserted_id, "ing_name": new_ing})
        else:
            recipe_id = request_data["recipe_id"]
            print("else")
            print(recipe_id)
            return display_edit_recipe(recipe_id)


# Menu to choose the ingredient and the action to perform
@app.route("/edit_ingredients")            
def edit_ingredients():

    # Connect to the SQLite3 datatabase
    cur = db_connect()
    cur.execute("SELECT * FROM ingredients ORDER BY name ASC")
    all_ingredients = cur.fetchall()
    # Close the connection
    db_close(cur)

    return render_template("edit_ingredients.html", all_ingredients=all_ingredients)

# Edit the ingredient name
@app.route("/edit_single_ingredient", methods=["GET", "POST"])
def edit_single_ingredient():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        ing_id = request.form.get("ing_id")
        ing_name = request.form.get("ing_name")
        if not ing_name:
            return render_template("result.html", msg="Please input a valid ingredient.")

        ing_name = ing_name.lower()

        try:
            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE ingredients SET name = ? WHERE id = ?", (ing_name, ing_id))
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
        ing_id = request.args.get("ing_id")
        
        # Connect to the SQLite3 datatabase
        cur = db_connect()
        cur.execute("SELECT * FROM ingredients WHERE id = ?", (ing_id,))
        ingredient = cur.fetchall()
        # Close the connection
        db_close(cur)

        return render_template("edit_single_ingredient.html", ingredient=ingredient)
    
# Delete the ingredient
@app.route("/delete_ingredient", methods=["GET", "POST"])
def delete_ingredient():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        ing_id = request.form.get("ing_id")
        try:
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('meal_planner.db') as con:
                    cur = con.cursor()
                    # Delete from 'ingredients' table 
                    cur.execute("DELETE FROM ingredients WHERE id = ?", (ing_id,))

                    # Commit the transaction
                    con.commit()
                    msg = "Record successfully deleted from the database"

        except Exception as e:
            # Rollback in case of error
            con.rollback()
            msg = "Error in the DELETE: " + str(e)

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

    else:
        ing_id = request.args.get("ing_id")

        # Connect to the SQLite3 datatabase
        cur = db_connect()

        cur.execute("SELECT * FROM ing_used WHERE ing_id = ?", (ing_id,))
        recipes = cur.fetchall()

        if recipes:
            return render_template('result.html', msg="This ingredient has associated recipes. It can not be deleted yet.")

        cur.execute("SELECT * FROM ingredients WHERE id = ?", (ing_id,))
        ingredient = cur.fetchall()


        # Close the connection
        db_close(cur)

        return render_template("delete_ingredient.html", ingredient=ingredient) 
    
# Menu to choose the ingredient and the action to perform
@app.route("/edit_units")            
def edit_units():
    # Connect to the SQLite3 datatabase
    cur = db_connect()
    cur.execute("SELECT * FROM units ORDER BY name ASC")
    all_units = cur.fetchall()
    # Close the connection
    db_close(cur)

    return render_template("edit_units.html", all_units=all_units)

# Edit the unit name
@app.route("/edit_single_unit", methods=["GET", "POST"])
def edit_single_unit():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        unit_id = request.form.get("unit_id")
        unit_name = request.form.get("unit_name")
        if not unit_name:
            return render_template("result.html", msg="Please input a valid unit.")

        unit_name = unit_name.lower()

        try:
            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('meal_planner.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE units SET name = ? WHERE id = ?", (unit_name, unit_id))
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
        unit_id = request.args.get("unit_id")
        
        # Connect to the SQLite3 datatabase
        cur = db_connect()
        cur.execute("SELECT * FROM units WHERE id = ?", (unit_id,))
        unit = cur.fetchall()
        # Close the connection
        db_close(cur)

        return render_template("edit_single_unit.html", unit=unit)
    
# Delete the unit
@app.route("/delete_unit", methods=["GET", "POST"])
def delete_unit():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        unit_id = request.form.get("unit_id")
        try:
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('meal_planner.db') as con:
                    cur = con.cursor()
                    
                    # Delete from 'units' table
                    cur.execute("DELETE FROM units WHERE id = ?", (unit_id,))

                    # Commit the transaction
                    con.commit()
                    msg = "Record successfully deleted from the database"

        except Exception as e:
            # Rollback in case of error
            con.rollback()
            msg = "Error in the DELETE: " + str(e)

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

    else:
        unit_id = request.args.get("unit_id")

        # Connect to the SQLite3 datatabase
        cur = db_connect()
        cur.execute("SELECT * FROM ing_used WHERE unit_id = ?", (unit_id,))
        recipes = cur.fetchall()

        if recipes:
            return render_template('result.html', msg="This unit has associated recipes. It can not be deleted yet.")
        
        cur.execute("SELECT * FROM units WHERE id = ?", (unit_id,))
        unit = cur.fetchall()
        # Close the connection
        db_close(cur)

        return render_template("delete_unit.html", unit=unit) 