import pymysql

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

with create_connection() as connection:
    with connection.cursor() as cursor:
            
            sql = """SELECT * FROM pokemon WHERE id = %s"""
            values = (600, )

            cursor.execute(sql, values)
            
            result = cursor.fetchone() #when you want to fetch everything in the database
            print(result["name"])
