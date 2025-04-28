from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("aboutme.html")

@app.route("/subjects")
def subjects():
    my_subjects = ["13COM", "13DTE", "13PHY", "13MTC", "13GEO"]
    return render_template("mysubjects.html", my_subjects=my_subjects)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/display", methods=["GET", "POST"])
def profile_result():
    fname=request.form["fname"] 
    email=request.form["email"]
    number=int(request.form["number"])
    address=request.form["address"]
    return render_template("display.html", fname=fname, email=email, number=number, address=address)

app.run(debug = True)

# you can use the .get funciton if there is going to be an optional/empty input in your form so the page wont crash
# request.form.get("fname")
# request.form.get("fname", "DEFAULT")