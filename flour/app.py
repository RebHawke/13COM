from flask import Flask, render_template, request, redirect, url_for, abort, flash, session
import pymysql
from datetime import datetime
import pymysql.err


app = Flask(__name__)
app.secret_key = 'PxH1#n!8'

def create_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        # host="10.0.0.17",
        # user="rebhawke",
        password="AFFIX",
        db="recipes",
        cursorclass=pymysql.cursors.DictCursor #what type of result info you want to come back (a list of all the fields, returning a list of dictionaries)

    )



@app.route("/")
def index():
    return render_template("home.html")

################################################################################################
################################# P R O F I L E S ##############################################
################################################################################################

@app.route("/accounts")
def account():
    return render_template("accounts.html")

# Login route
@app.route("/signup" , methods=["GET", "POST"])
def sign_up():
    if request.method == "POST": 

        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        skill = request.form["skill"]
        

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO profiles (name, username, password, email, skill) VALUES (%s, %s, %s, %s, %s)"
                values = (name, username, encrypt(password), email, skill)
                cursor.execute(sql, values)
                connection.commit()
                return redirect("/")
    return render_template("signup.html")

def encrypt(password):
    import hashlib #encodes the passowrd for security, creates a random string 
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM profiles WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, encrypt(password)))
            profile = cursor.fetchone()

        if profile:
            session['user_id'] = profile['user_id'] #user_id is what knows uf u are logged in
            session['name'] = profile['name']
            session['username'] = profile['username']  
            session['role'] = profile['role']  #admin, user, author
            flash("Logged In, Welcome " + (session['name']))
            return redirect("/")
        
        else:
            flash("Invalid Credentials")
            return render_template("login.html", error="Invalid credentials")
        

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear() #clears any logged in profiles
    return redirect("/")

################################################################################################
################################### R E C I P E S ##############################################
################################################################################################

@app.route("/recipe/create" , methods=["GET", "POST"])
def create():
    if 'role' not in session:
        flash("you do not have acess to this page")
        return redirect("/")
    else:
        if session['role'] == 'user':
            flash("you do not have acess to this page")
            return redirect("/")
        elif session['role'] != 'user':
            print(session['role'])
            if request.method == "POST": 

                name = request.form["name"]
                skill = request.form["skill"]
                date = datetime.now().date() #allows the program to find the date without the user needing to input date
                steps = request.form["steps"] #the ckeditor


                with create_connection() as connection:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO recipes (name, skill, date_posted, steps) VALUES (%s, %s, %s, %s)"
                        values = (name, skill, date, steps) #creates a more robust program using %s
                        cursor.execute(sql, values)
                        connection.commit()
                        return redirect("/")
            return render_template("create_recipe.html")



@app.route("/recipe/ingredients" , methods=["GET", "POST"]) #route displays the table with recipes, not adds ingredients to them
def ingredient():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes")
            recipes = cursor.fetchall()
    return render_template("ingredients.html", recipes=recipes)



@app.route("/add/ingredient-<int:id>", methods=["GET", "POST"]) #route displays ingredients avalible to add or create
def add_ingredients(id):
    connection = create_connection()
    with connection.cursor() as cursor:
        if request.method == "GET":
            sql = "SELECT * FROM recipes WHERE id = %s"
            cursor.execute(sql, (id,))
            recipe = cursor.fetchone()
    connection2 = create_connection()
    with connection2.cursor() as cursor:
        if request.method == "GET":
            sql = "SELECT * FROM ingredients"
            cursor.execute(sql, )
            ingredients = cursor.fetchall()
            return render_template('ingredient_list.html', recipe=recipe, ingredients=ingredients)


@app.route('/add_ingredient_to_recipe', methods=['POST']) #finally adds the ingredients
def add_ingredient_to_recipe():
    ingredient_id = request.form.get('ingredient_id')
    recipe_id = request.form.get('recipe_id')
    with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (%s, %s)"
                values = (recipe_id, ingredient_id)
                cursor.execute(sql, values)
                connection.commit()
                return redirect("/")
    

@app.route("/create_ingredient" , methods=["GET", "POST"])
def create_ingredient():
    if request.method == "POST": 
        
        name = request.form["name"]
        lowercase_name = name.lower() #ensures I cannot break the program with capital letters (for javascript searching)

        try:

            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO ingredients (name) VALUE (%s)"
                    value = (lowercase_name)
                    cursor.execute(sql, value)
                    connection.commit()
                    return redirect("/")

        except pymysql.err.DataError as e: #taught by ai, catches the error in pymysql, for too long it is classified as a data error
            if "1406" in str(e):  
                print("long")
                flash("Ingredient name is too long")
                return redirect("/")
        except pymysql.err.IntegrityError as e: #duplicate is an integrity error not data error so needs to be in a seperate statement
            if "1062" in str(e):  
                print("double")
                flash("Duplicate Ingredient")
                return redirect("/")
    return redirect("/")


app.run(debug = True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)