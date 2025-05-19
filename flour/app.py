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
        
        try:
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO profiles (name, username, password, email, skill) VALUES (%s, %s, %s, %s, %s)"
                    values = (name, username, encrypt(password), email, skill)
                    cursor.execute(sql, values)
                    connection.commit()

                    with connection.cursor() as cursor:
                        sql = "SELECT * FROM profiles WHERE username = %s AND password = %s"
                        cursor.execute(sql, (username, encrypt(password)))
                        profile = cursor.fetchone()

                    session['user_id'] = profile['user_id'] #user_id is what knows uf u are logged in
                    session['name'] = profile['name']
                    session['username'] = profile['username']  
                    session['role'] = profile['role']  #admin, user, author
                    flash("Logged In, Welcome " + (session['name']))

                    return redirect("/profiles")
        except pymysql.err.IntegrityError as e: #duplicate is an integrity error not data error so needs to be in a seperate statement
            if "1062" in str(e):  
                print("double")
                flash("Duplicate name")
                return redirect("/")        
        

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
            return redirect("/profiles")
        
        else:
            flash("Invalid Credentials")
            return render_template("login.html", error="Invalid credentials")
        
@app.route("/profiles")
def profile():
    if 'user_id' in session:
        name = session['name']
        id = session['user_id']
        username = session['username']
        return render_template("profile.html", name=name, id=id, username=username)
    else:
        return redirect("/accounts")


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

            connection2 = create_connection()
            with connection2.cursor() as cursor:
                with connection2.cursor() as cursor:
                    if request.method == "GET":
                        sql = "SELECT * FROM ingredients"
                        cursor.execute(sql, )
                        ingredients = cursor.fetchall()

            if request.method == "POST": 
                print(request.form.getlist('ingredient_id'))
                name = request.form["name"]
                skill = request.form["skill"]
                date = datetime.now().date() #allows the program to find the date without the user needing to input date
                steps = request.form["steps"] #the ckeditor
                
                ingredient_id = request.form.getlist('ingredient_id')


                with create_connection() as connection:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO recipes (name, skill, date_posted, steps) VALUES (%s, %s, %s, %s)"
                        values = (name, skill, date, steps) #creates a more robust program using %s
                        cursor.execute(sql, values)
                        recipe_id = cursor.lastrowid

                        for ingredient in ingredient_id:
                            sql2 = "INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (%s, %s)"
                            values2 = (recipe_id, ingredient)  
                            cursor.execute(sql2, values2)
                        print("Last inserted row ID:", )
                        connection.commit()
                        flash("recipe created")
                        return redirect("/")
            return render_template("create_recipe.html", ingredients = ingredients)

    

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