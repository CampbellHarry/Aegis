from flask import Flask, render_template, redirect, request, session
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session security

# Custom decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def root():
    if "username" in session:
        return redirect("/index")
    return redirect("/login")

@app.route("/index")
@login_required
def index():
    return render_template("index.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/index")  # Redirect to index if user is already logged in
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Connect to the database
        conn = sqlite3.connect("members.db")  # Change the filename as needed
        cursor = conn.cursor()
        
        # Check if the user exists and password matches
        query = "SELECT * FROM users WHERE email = ? AND password = ?"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        
        if user:
            session["username"] = user[0]  # Store username in session
        else:
            # If the user is not found, create a new account
            cursor.execute("INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)", (email, password))
            session["username"] = email
        
        conn.commit()
        conn.close()
        
        return redirect("/index")

    return render_template("login.html")

# Logout route
@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
