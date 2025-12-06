from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "rahasia_brow"

def db():
    return sqlite3.connect("database.db")

# =========================
# DATABASE INIT
# =========================
with db() as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            kategori TEXT,
            judul TEXT,
            email TEXT,
            password TEXT
        )
    """)

# =========================
# REGISTER
# =========================
@app.route("/", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pw = hashlib.sha256(request.form["password"].encode()).hexdigest()

        with db() as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?,?)",
                (user, pw)
            )

        return redirect("/login")

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = request.form["username"]
        pw = hashlib.sha256(request.form["password"].encode()).hexdigest()

        with db() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (user, pw)
            )
            data = c.fetchone()

        if data:
            session["user"] = data[0]
            return redirect("/dashboard")
        else:
            error = "Username atau password salah!"

    return render_template("login.html", error=error)

# =========================
# DASHBOARD + ADD GAME DATA
# =========================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    # ADD DATA GAME
    if request.method == "POST":
        kategori = request.form["kategori"]
        judul = request.form["judul"]
        email = request.form["email"]
        password = request.form["password"]

        with db() as conn:
            conn.execute(
                "INSERT INTO data (user_id, kategori, judul, email, password) VALUES (?,?,?,?,?)",
                (session["user"], kategori, judul, email, password)
            )

    with db() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, kategori, judul, email, password FROM data WHERE user_id=?",
            (session["user"],)
        )
        all_data = c.fetchall()

    return render_template("dashboard.html", data=all_data)

# =========================
# ADD EMAIL DATA (KHUSUS 2 INPUT)
# =========================
@app.route("/add-email", methods=["POST"])
def add_email():
    if "user" not in session:
        return redirect("/login")

    email = request.form["email"]
    password = request.form["password"]
    kategori = "Email"

    with db() as conn:
        conn.execute(
            "INSERT INTO data (user_id, kategori, judul, email, password) VALUES (?,?,?,?,?)",
            (session["user"], kategori, "-", email, password)
        )

    return redirect("/dashboard")

# =========================
# DELETE DATA
# =========================
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    with db() as conn:
        conn.execute(
            "DELETE FROM data WHERE id=? AND user_id=?",
            (id, session["user"])
        )

    return redirect("/dashboard")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()



