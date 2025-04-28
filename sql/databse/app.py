from flask import Flask, render_template, request, session, redirect
import pymysql

app = Flask(__name__)

def create_connection():
    return pymysql.connect(
        # host="localhost",
        # user="root",
        host="10.0.0.17",
        user="rebhawke",
        password="AFFIX",
        db="pokemon_2025",
        cursorclass=pymysql.cursors.DictCursor #what type of result info you want to come back (a list of all the fields, returning a list of dictionaries)

    )

@app.route("/")
def index():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM pokemon")
            result = cursor.fetchall()
    return render_template("index.html", result=result)


@app.route("/view")
def view():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM pokemon WHERE id = %s"
            values = (request.args["id"],)
            cursor.execute(sql, values)
# structure the sql and vlaues and cursor bit like this to ensure it is secure and others are unable to steal info/delete info
            result = cursor.fetchone()
    return render_template("view.html", pokemon=result)

app.run('0.0.0.0', 5555, debug=True)
