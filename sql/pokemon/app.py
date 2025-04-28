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

@app.route("/delete")
def delete():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM pokemon")
            result = cursor.fetchall()
    return render_template("edit.html", result=result)

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

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":    
        name = request.form["name"]
        image = request.form["image"]
        number = request.form["number"]
        generation = request.form["generation"]
        type1 = request.form["type1"]
        type2 = request.form.get("type2")
        health = request.form["health"]
        attack = request.form["attack"]
        defence = request.form["defence"]
        special_attack = request.form["special_attack"]
        special_defence = request.form["special_defence"]
        speed = request.form["speed"]

        with create_connection() as connection:
            with connection.cursor() as cursor:
                if type2 != "empty":
                    sql = "INSERT INTO pokemon (name, image, number, generation, type1, type2, health, attack, defence, special_attack, special_defence, speed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (name, image, number, generation, type1, type2, health, attack, defence, special_attack, special_defence, speed)
                else:
                    sql = "INSERT INTO pokemon (name, image, number, generation, type1, health, attack, defence, special_attack, special_defence, speed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (name, image, number, generation, type1, health, attack, defence, special_attack, special_defence, speed)
                cursor.execute(sql, values)
                connection.commit()
    return render_template("add.html")

@app.route("/delete-pokemon-<int:id>", methods=["GET", "POST"])
def delete_pokemon(id):
    connection = create_connection()
    with connection.cursor() as cursor:
        if request.method == "GET":
            sql = "SELECT * FROM pokemon WHERE id = %s"
            cursor.execute(sql, (id,))
            pokemon = cursor.fetchone()

            if pokemon:
                return render_template('confirm_delete.html', pokemon=pokemon)
            else:
                return "Pokémon not found.", 404
            
        # If method is POST, delete the Pokémon
        if request.method == "POST":
            sql = "DELETE FROM pokemon WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()  # Ensure the changes are committed to the database
            
            return redirect("/")  # Redirect to the Pokémon list page or any other desired route
        
@app.route("/edit")
def edit_pokemon():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM pokemon")
            result = cursor.fetchall()
    return render_template("edit.html", result=result)
        
@app.route("/edit-pokemon-<int:id>", methods=["GET", "POST"])
def edit(id):
  connection = create_connection()
  with connection.cursor() as cursor:
    if request.method == "GET":
      sql = "SELECT * FROM pokemon WHERE id = %s"
      cursor.execute(sql, (id,))
      pokemon = cursor.fetchone()
      print(pokemon)
      return render_template("confirm_edit.html", pokemon = pokemon)

    if request.method == "POST":
        name = request.form["name"]
        image = request.form["image"]
        number = request.form["number"]
        generation = request.form["generation"]
        type1 = request.form["type1"]
        type2 = request.form.get("type2")
        health = request.form["health"]
        attack = request.form["attack"]
        defence = request.form["defence"]
        special_attack = request.form["special_attack"]
        special_defence = request.form["special_defence"]
        speed = request.form["speed"]

    with create_connection() as connection:
        with connection.cursor() as cursor:
            if type2 != "empty":
                values = (name, image, number, generation, type1, type2, health, attack, defence, special_attack, special_defence, speed, id)
                sql = """UPDATE pokemon 
                        SET name = %s, image = %s, number = %s, generation = %s, type1 = %s, type2 = %s, health = %s, attack = %s, defence = %s, special_attack = %s, special_defence = %s, speed = %s
                        WHERE id = %s"""
            else:
                values = (name, image, number, generation, type1, health, attack, defence, special_attack, special_defence, speed, id)
                sql = """UPDATE pokemon 
                        SET name = %s, image = %s, number = %s, generation = %s, type1 = %s, health = %s, attack = %s, defence = %s, special_attack = %s, special_defence = %s, speed = %s
                        WHERE id = %s"""
            
            cursor.execute(sql, values)
            connection.commit()

    return redirect("/")  





app.run('0.0.0.0', 5555, debug=True)

# DELETE FROM `pokemon_2025`.`pokemon` WHERE (`id` = '1250');