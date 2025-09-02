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
def home():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes WHERE featured = 'true'")
            featured = cursor.fetchall()
    return render_template("home.html", featured=featured)

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
                    cursor.execute(sql, values) #safter way to input variables as less prone to tampering
                    connection.commit()

                    with connection.cursor() as cursor:
                        sql = "SELECT * FROM profiles WHERE username = %s AND password = %s"
                        cursor.execute(sql, (username, encrypt(password)))
                        profile = cursor.fetchone()

                    session['user_id'] = profile['user_id'] #user_id is what knows if u are logged in
                    session['name'] = profile['name']
                    session['username'] = profile['username']  
                    session['role'] = profile['role']  
                    session['email'] = profile['email']
                    session['skill'] = profile['skill']
                    flash("Logged In, Welcome " + (session['name']))

                    return redirect("/profiles")
        except pymysql.err.IntegrityError as e: #duplicate is an integrity error not data error so needs to be in a seperate statement
            if "1062" in str(e):  #found by causing the error and reding the message
                print("double")
                flash("Duplicate name")
                return redirect("/")        
        

def encrypt(password):
    import hashlib #encodes the passowrd for security, creates a random string 
    return hashlib.sha256(password.encode()).hexdigest() #type of encoding


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM profiles WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, encrypt(password))) #changes password to encrypted
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

        connection = create_connection()
        with connection.cursor() as cursor: #joins the user id to the recipe id likes so i can filter for only one profile likes
            sql = "SELECT * FROM recipes JOIN likes ON recipes.id = likes.recipe_id WHERE likes.user_id = %s"
            cursor.execute(sql, (id,))
            result = cursor.fetchall()

        return render_template("profile.html", name=name, id=id, username=username, email=email, skill=skill, result=result)
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

        # redefine session variables
        session["name"] = updated["name"]
        session["username"] = updated["username"]
        session["email"] = updated["email"]
        session["skill"] = updated["skill"]

    return redirect("/profiles")

@app.route('/account/delete/admin', methods=['POST'])
def delete_user_route():
    connection = create_connection()
    with connection.cursor() as cursor:
        if "role" in session and session["role"] == "admin":  
            user_id = request.form["user_id"] 
            sql = "DELETE FROM profiles WHERE user_id = %s"  
            cursor.execute(sql, (user_id,)) #user id is passed invisible
            connection.commit()
            return redirect('/users')
        else:
            return "Unauthorized", 404
        
@app.route('/account/update/admin', methods=['POST'])
def update_user_route():
    connection = create_connection()
    with connection.cursor() as cursor:
        if "role" in session and session["role"] == "admin":  #checks admin is logged in
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
            user_id = session.get('user_id')  
            if user_id:  #makes sure someone is logged in
                sql = "DELETE FROM profiles WHERE user_id = %s"  
                cursor.execute(sql, (user_id,))  
                connection.commit()

    #remove logged in profiles
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
    user_id = session.get("user_id")
    liked = False
    with create_connection() as connection2:
        with connection2.cursor() as cursor:
            sql = "SELECT * FROM likes WHERE recipe_id = %s AND user_id = %s"
            cursor.execute(sql, (recipe_id, user_id))
            if cursor.fetchone():
                liked = True 
    with create_connection() as connection3:
        with connection3.cursor() as cursor:
            sql = "SELECT recipes.*, COUNT(likes.id) AS likes FROM recipes LEFT JOIN likes ON recipes.id = likes.recipe_id WHERE recipes.id = %s GROUP BY recipes.id"
            cursor.execute(sql, (recipe_id,))
            result = cursor.fetchone()
    if not result:
        return abort(404) #passes an error for my error page
            
    return render_template("view.html", recipe=result, liked=liked)

@app.route("/recipe/like", methods=["GET", "POST"])
def like():
    recipe_id = request.form.get("recipe_id")
    user_id = session.get('user_id')
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO likes (recipe_id, user_id) VALUES (%s, %s)"
            cursor.execute(sql, (recipe_id, user_id))
            connection.commit()
            return redirect(url_for("view", id=recipe_id))  ##### ai taught me how to do this so i could reload with the existing id as no return reload function exists
    with create_connection() as connection2:
        with connection2.cursor() as cursor:
            sql = "SELECT * FROM recipes WHERE id = %s"
            cursor.execute(sql, (recipe_id,))
            result = cursor.fetchone()
    return render_template("view.html", recipe=result)

@app.route("/recipe/un-like", methods=["GET", "POST"])
def unlike():
    recipe_id = request.form.get("recipe_id")
    user_id = session.get('user_id')
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM likes WHERE recipe_id = %s AND user_id = %s"
            cursor.execute(sql, (recipe_id, user_id))
            connection.commit()
    return redirect(url_for("view", id=recipe_id))



@app.route("/edit_recipes")
def edit_recipes():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes")
            result = cursor.fetchall()
    return render_template("edit_recipes.html", result=result)
        
@app.route("/edit-recipes-<int:id>", methods=["GET", "POST"])
def edit(id):
  connection = create_connection()
  with connection.cursor() as cursor:
    if request.method == "GET":
      sql = "SELECT * FROM recipes WHERE id = %s"
      cursor.execute(sql, (id,))
      recipe = cursor.fetchone()
      print(recipe)
      return render_template("recipe_editor.html", recipe = recipe)

    if request.method == "POST":
        recipe_id = request.form["recipe_id"]
        name = request.form["name"]
        image = request.form["image"]
        skill = request.form["skill"]
        featured = request.form["featured"]

    with create_connection() as connection:
        with connection.cursor() as cursor:
            values = (name, image, skill, featured, recipe_id)
            sql = """UPDATE recipes 
                    SET name = %s, image = %s, skill = %s, featured = %s
                    WHERE id = %s"""

            cursor.execute(sql, values)
            connection.commit()

    return redirect("/")  


@app.route("/recipe/create" , methods=["GET", "POST"])
def create():
    if 'role' not in session:
        flash("you do not have acess to this page")
        return redirect("/")
    else:
        if session['role'] == 'user':
            flash("you do not have acess to this page")
            return redirect("/")
        elif session['role'] != 'user': #if session role not user
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
                
                ingredient_id = request.form.getlist('ingredient_id') #getlist because there can be more than one


                with create_connection() as connection:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO recipes (name, skill, date_posted, steps, image) VALUES (%s, %s, %s, %s, %s)"
                        values = (name, skill, date, steps, image) #creates a more robust program using %s
                        cursor.execute(sql, values)
                        recipe_id = cursor.lastrowid #allows me to use the recipe id before the recipe has been created as the forms are submitted at the same time

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

        except pymysql.err.DataError as e: #catches the error in pymysql, for too many characters, it is classified as a data error
            if "1406" in str(e):  
                print("long")
                flash("ingredient name is too long")
                return redirect("/")
        except pymysql.err.IntegrityError as e: #duplicate is an integrity error not data error so needs to be in a seperate statement
            if "1062" in str(e):  
                print("double")
                flash("duplicate Ingredient")
                return redirect("/")
    return redirect("/")


# @app.errorhandler(404) #error handling, redirect page for 404 errors
# def fnf(err):
#     return render_template("error.html")



app.run(debug = True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)