from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = "pcws800"

@app.route("/", methods = ['POST', 'GET'])
def index():
    if ("message" in session) and (session["message"] == "hello"):
        print("this user has visited this page already")
    session["message"] = "hello"
    temp = None
    result = None
    tempunit = None
    if request.method == "POST":
        temp = request.form.get("tempinput")
        tempunit = request.form.get("tempunit")  

        if tempunit == "celsius":
            result = ((int(temp)*1.8) + 32)
        elif tempunit == "fahrenheit":
            result = ((int(temp)-32) / 1.8)
    return render_template("/index.html", temp=temp, result=result, tempunit=tempunit)

@app.route("/name", methods = ['POST', 'GET'])
def name():
    fname = None
    if request.method == "POST":
        fname = request.form.get("fname")
    return render_template("/name.html", fname=fname)

@app.route("/temp", methods = ['POST', 'GET'])
def temp():
    temp = None
    faren = None
    if request.method == "POST":
        temp = request.form.get("temp")
        faren = ((int(temp)*1.8) + 32)
    return render_template("/temp.html", temp=temp, faren=faren)

@app.route("/game", methods = ['POST', 'GET'])
def game():
    num = 0
    compnum = 0
    snum = 0
    scompnum = 0

    if 'numberstack' not in session:
        session['numberstack'] = '0'

    if request.method == "POST":
        snum = request.form.get("start", 0)
        if snum:
            scompnum = (12- int(snum)) 
            session['numberstack'] += "|" + str(snum)
            session['numberstack'] += "|" + str(scompnum)
        else:
    
            num = request.form.get("num", 0)
            compnum = (11- int(num)) 
            session['numberstack'] += "|" + str(num)
            session['numberstack'] += "|" + str(compnum)
# make a starting numebr question and the 100max
    total = sum( int(n) for n in session['numberstack'].split("|") )

    return render_template("/game.html", num=num, compnum=compnum, numberstack=session['numberstack'], total = total, snum=snum, scompnum=scompnum)

@app.route("/page1")
def page1():
    if "count" not in session:
        session["count"] = 1
    else:
        session["count"] = int(session["count"]) + 1

    return render_template("/session.html", session=session)

@app.route("/page3")
def page3():
    session.clear()
    return redirect("/")


app.run('0.0.0.0', 5555, debug=True)
