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
                    session['email'] = profile['email']
                    session['skill'] = profile['skill']
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
            session['email'] = profile['email']  
            session['skill'] = profile['skill']  
            flash("Logged In, Welcome " + (session['name']))
            return redirect("/profiles")
        
        else:
            flash("Invalid Credentials")
            return render_template("accounts.html", error="Invalid credentials")
        
@app.route("/profiles")
def profile():
    if 'user_id' in session:
        name = session['name']
        id = session['user_id']
        username = session['username']
        email = session['email']
        skill = session['skill']
        return render_template("profile.html", name=name, id=id, username=username, email=email, skill=skill)
    else:
        return redirect("/accounts")
    

@app.route("/account/edit", methods=["GET", "POST"])
def acc_edit():
    connection = create_connection()
    
    if request.method == "POST":
        user_id = session.get("user_id")
        if not user_id:
            return redirect("/accounts")

        with connection.cursor() as cursor:
            cursor.execute("SELECT name, username, email, skill FROM profiles WHERE user_id = %s", (user_id,))
            current_profile = cursor.fetchone()

        name = request.form.get("name") or current_profile["name"]
        username = request.form.get("username") or current_profile["username"]
        email = request.form.get("email") or current_profile["email"]
        skill = request.form.get("skill") or current_profile["skill"]

        with connection.cursor() as cursor:
            sql = "UPDATE profiles SET name = %s, username = %s, email = %s, skill = %s WHERE user_id = %s"
            cursor.execute(sql, (name, username, email, skill, user_id))
            connection.commit()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, username, email, skill FROM profiles WHERE user_id = %s", (user_id,))
            updated = cursor.fetchone()

        # Refresh session variables
        session["name"] = updated["name"]
        session["username"] = updated["username"]
        session["email"] = updated["email"]
        session["skill"] = updated["skill"]

    return redirect("/profiles")

@app.route('/account/delete/admin', methods=['POST'])
def delete_user_route():
    connection = create_connection()
    with connection.cursor() as cursor:
        if "role" in session and session["role"] == "admin":  # Ensure admin is logged in
            user_id = request.form["user_id"]  # Get the user ID from the form
            sql = "DELETE FROM profiles WHERE user_id = %s"  # Use parameterized query correctly
            cursor.execute(sql, (user_id,))  # Pass user_id correctly
            connection.commit()
            return redirect('/users')
        else:
            return "Unauthorized", 403
        
@app.route('/account/update/admin', methods=['POST'])
def update_user_route():
    connection = create_connection()
    with connection.cursor() as cursor:
        if "role" in session and session["role"] == "admin":  # Ensure admin is logged in
            new_role = request.form["role"]
            edit_user_id = request.form["user_id"]  
            sql = "UPDATE profiles SET role = %s WHERE user_id = %s"  
            cursor.execute(sql, (new_role, edit_user_id))  
            connection.commit()
            return redirect('/users')
        else:
            return "Unauthorized", 403




@app.route("/account/delete", methods=["GET", "POST"])
def acc_delete():
    connection = create_connection()
    with connection.cursor() as cursor:
        if request.method == "POST":
            user_id = session.get('user_id')  # Properly retrieve the user ID
            if user_id:  # Ensure user_id exists in session
                sql = "DELETE FROM profiles WHERE user_id = %s"  # Use parameterized query correctly
                cursor.execute(sql, (user_id,))  # Pass user_id correctly
                connection.commit()

    # Clears any logged-in profiles
    session.clear()
    return redirect("/")

@app.route("/users")
def users():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM profiles")
            result = cursor.fetchall()
    return render_template("users.html", result=result)

@app.route("/logout")
def logout():
    session.clear() #clears any logged in profiles
    return redirect("/")

################################################################################################
################################### R E C I P E S ##############################################
################################################################################################

@app.route("/all")
def all():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes")
            result = cursor.fetchall()
    return render_template("index.html", result=result)

@app.route("/view")
def view():
    recipe_id = request.args.get("id")
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM recipes WHERE id = %s"
            cursor.execute(sql, (recipe_id,))
            result = cursor.fetchone()
    return render_template("view.html", recipes=result)


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
                date = datetime.now().date() 
                steps = request.form["steps"] 
                image = request.form["image"]
                
                ingredient_id = request.form.getlist('ingredient_id')


                with create_connection() as connection:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO recipes (name, skill, date_posted, steps, image) VALUES (%s, %s, %s, %s, %s)"
                        values = (name, skill, date, steps, image) #creates a more robust program using %s
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

    

@app.route("/ingredient/create" , methods=["GET", "POST"])
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
                    return redirect("/recipe/create")

        except pymysql.err.DataError as e: #taught by ai, catches the error in pymysql, for too many characters, it is classified as a data error
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