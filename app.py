from flask import Flask, render_template, request, session, redirect
from flask_session import Session
import sqlite3

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    key = request.args.get("q")
    key = key.strip()
    key = "%" + key + "%"
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT drugs.drug_name, drugs.rowid, pharmacies.pharmacy_name, pharmacies.pharmacy_address, pharmacies.rowid FROM stocks JOIN drugs ON stocks.drug_id=drugs.rowid JOIN pharmacies ON stocks.pharmacy_id=pharmacies.rowid WHERE drugs.drug_name LIKE ? AND stocks.quantity > 0", (key,))
    results = c.fetchall()
    conn.close()
    return render_template("search.html", results=results)

@app.route("/drug", methods=["POST"])
def drug():
    pharmacy_id = request.form.get("pharmacy-id")
    drug_id = request.form.get("drug-id")
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM drugs WHERE rowid=?", (drug_id,))
    drugs = c.fetchall()
    c.execute("SELECT * FROM pharmacies WHERE rowid=?", (pharmacy_id,))
    pharmacies = c.fetchall()
    return render_template("drug.html", drug=drugs[0], pharmacy=pharmacies[0])

@app.route("/pharmacist")
def pharmacist():
    if not session.get("email"):
        return render_template("pharmacist_login.html")
    else:
        return render_template("pharmacist_main.html")

@app.route("/pharma_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("SELECT * FROM pharmacies WHERE email LIKE ? AND password=?", (email, password))
        l = c.fetchall()
        if len(l) > 0:
            session["email"] = email
            return redirect("/pharmacist")
    return render_template("pharmacist_login.html")

@app.route("/pharma_logout")
def logout():
    session["email"] = None
    return redirect("/")
