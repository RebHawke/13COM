from flask import Flask, render_template, request, session, redirect, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'password'


def create_connection():
    return pymysql.connect(
        # host="localhost",
        # user="root",
        host="10.0.0.17",
        user="rebhawke",
        password="AFFIX",
        db="rebhawke_bark",
        cursorclass=pymysql.cursors.DictCursor #what type of result info you want to come back (a list of all the fields, returning a list of dictionaries)

    )

role_redirects = {
    'admin': '/admin',
    'user': '/user',
    'guest': '/guest'
}


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST": 
        import uuid    #uuid is a python random library
        import os
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        randomness = str(uuid.uuid4()) [:8] #:8 is 0-8 characters/first 8
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        profile = request.files["profile"]

        filepath = "static/images/" + randomness + '-' + profile.name
        profile.save(filepath)
        filepath = "/" + filepath
        

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (name, username, password, profile) VALUES (%s, %s, %s, %s)"
                values = (name, username, encrypt(password), filepath)
                cursor.execute(sql, values)
                connection.commit()
                flash("You are now signed up")
                return redirect("/login")
    return render_template("signup.html")

def encrypt(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, encrypt(password)))
            user = cursor.fetchone()

        if user:
            session['user_id'] = user['id'] #staff_id is user_id which is what knows uf u are logged in
            session['name'] = user['name']
            session['username'] = user['username']  
            session['role'] = user['role']  
            flash("Log In Successful")
            return redirect("/")
        else:
            flash("Invalid credentials")
            return render_template("login.html", error="Invalid credentials")
        

    return render_template("login.html")

@app.route("/secret")
def secret():
    if 'user_id' not in session:
        flash("You do not have access")
        return redirect("/") 
    else:
        flash("You made it!")
        return render_template("secret.html")
    
##################################################### E D I T   U S E R S ####################################################


@app.route("/delete")
def delete():
    if session.get("role") == "admin":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "DELETE FROM users WHERE id=%s"
                values = (request.args['id'])
                cursor.execute(sql, values)
                connection.commit()
                return redirect("/admin")
    else:
        flash("You don't have permission to access this page")
        return redirect("/")

@app.route("/revoke")
def revoke():
    if session.get("role") == "admin":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET role='user' WHERE id=%s"
                values = (request.args['id'])
                cursor.execute(sql, values)
                connection.commit()
                return redirect("/admin")
    else:
        flash("You don't have permission to access this page")
        return redirect("/")

@app.route("/grant")
def grant():
    if session.get("role") == "admin":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET role='admin' WHERE id=%s"
                values = (request.args['id'])
                cursor.execute(sql, values)
                connection.commit()
                return redirect("/admin")
    else:
        flash("You don't have permission to access this page")
        return redirect("/")
     
 ##################################################### L O G O U T ####################################################
 

@app.route("/logout")
def logout():
    session.clear() #clears any logged in profiles
    return redirect("/")

##################################################### U S E R S   P A G E S ####################################################


@app.route("/role")
def role():
    role = session.get('role', 'guest')
    redirect_route = role_redirects.get(role, '/guest-page')
    return redirect(redirect_route)

@app.route("/admin")
def admin():
    if session.get("role") == "admin":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users"
                cursor.execute(sql)
                result = cursor.fetchall()
                return render_template("admin-page.html", result=result)
    else:
        flash("You don't have permission to access this page")
        return redirect("/")

@app.route("/user")
def user_page():
    return "User page"

@app.route("/guest")
def guest_page():
    return "Guest page"

##################################################### P O S T S ####################################################

@app.route("/posts/add", methods=["GET", "POST"])
def posts_add():
    if request.method == "POST":    
        id = session['user_id']
        content = request.form["content"]

        with create_connection() as connection:
            with connection.cursor() as cursor:
                # fetch_id = "SELECT id FROM users WHERE name = %s" 
                # cursor.execute(fetch_id, (name,))
                # found_id = cursor.fetchone()['id']
                
                # select = "SELECT * FROM posts JOIN users ON posts.userid = users.id" 

                sql = "INSERT INTO posts (userid, content) VALUES (%s, %s)"
                values = (id, content)
                cursor.execute(sql, values)
                connection.commit()
                flash("Your post has been created")
                return redirect("/")
    return render_template("post_add.html")

@app.route("/posts/view")
def posts_view():
    connection = create_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM posts JOIN users ON posts.userid = users.id")
        posts = cursor.fetchall()
    return render_template("view.html", posts=posts)

@app.route("/posts/delete-<int:id>", methods=["GET", "POST"])
def posts_delete(id):
    connection = create_connection()
    with connection.cursor() as cursor:
        if request.method == "GET":
            sql = "SELECT * FROM posts WHERE id = %s"
            cursor.execute(sql, (id,))
            posts = cursor.fetchone()

            if posts:
                return render_template('confirm_delete.html', posts=posts)
            else:
                return "post not found.", 404
            
        # If method is POST, delete the Pokémon
        if request.method == "POST":
            sql = "DELETE FROM posts WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()  # Ensure the changes are committed to the database
            
            return redirect("/")  # Redirect to the Pokémon list page or any other desired route

@app.route("/posts/edit-<int:id>")
def posts_edit():
    ...

app.run('0.0.0.0', 5555, debug=True)
