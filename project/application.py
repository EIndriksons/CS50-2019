from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, login_admin_required, apology

""" Configuration """

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


""" Website """

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/finance")
@login_required
def finance():
    """ Private 'Finance' board """

    # SELECT for the list of finance forms in main 'Finance' page
    finances = db.execute("SELECT id, date, number, status, name_director, name_accountant FROM Finance WHERE user_id = :user_id ORDER BY date",
        user_id=session["user_id"])

    return render_template("finance.html", finances=finances)


@app.route("/create_form")
@login_required
def finance_form_new():
    """ Create Finance Form """

    # TODO implement anti-spamming control which checks DB for the last form entry

    # SELECT for the default information
    info = db.execute("SELECT name_director, name_accountant FROM Settings ORDER BY id desc LIMIT 1")

    # INSERT new Finance form with default values
    finance = db.execute("INSERT INTO Finance (user_id, status, name_director, name_accountant) VALUES(:user_id, :status, :name_director, :name_accountant)",
            user_id=session["user_id"],
            status="Draft",
            name_director=info[0]["name_director"],
            name_accountant=info[0]["name_accountant"])

    if not finance:
        return jsonify(False)

    return jsonify(True)


@app.route("/finance/<finance_id>", methods=["GET", "POST"])
@login_required
def finance_form(finance_id):
    """ Individual Finance form """

    if request.method == "POST":

        # Checking for Admin user
        if session["role"] == 'Admin':

            # UPDATE for Finance Form information
            finance = db.execute("UPDATE Finance SET status=:status, number=:number, date=:date, text=:text, name_director=:name_director, name_accountant=:name_accountant WHERE id=:finance_id",
                    status=request.form.get("status"),
                    number=request.form.get("number"),
                    date=request.form.get("date"),
                    text=request.form.get("text"),
                    name_director=request.form.get("name_director"),
                    name_accountant=request.form.get("name_accountant"),
                    finance_id=finance_id)

        # If not Admin user
        else:

            finance = db.execute("UPDATE Finance SET status=:status, number=:number, date=:date, text=:text WHERE id=:finance_id",
                    status=request.form.get("status"),
                    number=request.form.get("number"),
                    date=request.form.get("date"),
                    text=request.form.get("text"),
                    finance_id=finance_id)

        return redirect("/finance/" + str(finance_id))

    else:

        # SELECT for Finance Form information and list of Transactions
        finance = db.execute("SELECT f.id, f.user_id, u.name || ' ' || u.surname as username, f.date, f.number, f.status, f.text, f.name_director, f.name_accountant FROM Finance f LEFT JOIN Users u ON u.id = f.user_id WHERE f.id=:id",
                    id=finance_id)
        transactions = db.execute("SELECT id, status, date, partner, expense, amount FROM Transactions WHERE finance_id=:finance_id",
                    finance_id=finance_id)

        # Check if the User is the one logged in correct
        if session["user_id"] != finance[0]["user_id"]:
            return redirect("/")

        return render_template("finance_form.html", finance=finance, transactions=transactions)


@app.route("/finance/<finance_id>/create_transaction", methods=["GET"])
@login_required
def finance_transaction_new(finance_id):
    """ Create New Transaction """

    # TODO implement anti-spamming control which checks DB for the last form entry

    # INSERT for blank Transaction in the database
    transaction = db.execute("INSERT INTO Transactions (finance_id, status) VALUES(:finance_id, :status)",
                finance_id=finance_id,
                status="Draft")

    # TODO FLASH MESSAGE
    flash("Password Changed!")
    return jsonify(True)


@app.route("/finance/<finance_id>/<transaction_id>", methods=["GET", "POST"])
@login_required
def finance_transaction(finance_id, transaction_id):
    """ Individual Finance transaction """

    if request.method == "POST":

        # UPDATE for Transaction information
        transaction = db.execute("UPDATE Transactions SET date=:date, partner=:partner, expense=:expense, amount=:amount WHERE id=:transaction_id",
                    date=request.form.get("date"),
                    partner=request.form.get("partner"),
                    expense=request.form.get("expense"),
                    amount=request.form.get("amount"),
                    transaction_id=transaction_id)

        return redirect("/finance/" + str(finance_id) + '/' + str(transaction_id))

    else:

        # SELECT for finance transaction information
        transaction = db.execute("SELECT id, finance_id, status, date, partner, expense, amount FROM Transactions WHERE id = :id",
            id=transaction_id)

        return render_template("finance_transaction.html", transaction=transaction)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
@login_admin_required
def dashboard():
    """ Admin Finance board"""

    dashboards = db.execute("SELECT user_id, date, number, status, name_director, name_accountant, id FROM Finance ORDER BY date")

    return render_template("dashboard.html", dashboards=dashboards)


@app.route("/dashboard/<finance_id>", methods=["GET", "POST"])
@login_required
@login_admin_required
def dashboard_form(finance_id):
    """ Individual Finance template for Admin board """

    # Query for finance form information
    dashboard = db.execute("SELECT id, user_id, date, number, status, name_director, name_accountant FROM Finance WHERE id = :id",
        id=finance_id)

    return render_template("dashboard_form.html", dashboard=dashboard)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """ Settings """
    return render_template("index.html")

@app.route("/admin_settings", methods=["GET", "POST"])
@login_required
@login_admin_required
def admin_settings():
    """ Admin Settings """

    if request.method == "POST":

        # SANITIZE INPUTS
        db.execute("INSERT INTO Settings (name_director, name_accountant) VALUES (:name_director, :name_accountant)",
            name_director=request.form.get("name_director"),
            name_accountant=request.form.get("name_accountant"))

        # Query for info
        info = db.execute("SELECT name_director, name_accountant FROM Settings ORDER BY id desc LIMIT 1")
        return render_template("admin_settings.html", info=info)

    else:
        # Query for info
        info = db.execute("SELECT name_director, name_accountant FROM Settings ORDER BY id desc LIMIT 1")
        return render_template("admin_settings.html", info=info)


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register """

    if request.method == "POST":

        # Create hash from password
        hash = generate_password_hash(request.form.get("password"))

        # TODO:
        # Check for unique ID in database
        # Check that HASH cannot be NULL

        # Insert user in database
        new_user = db.execute("INSERT INTO Users (email, name, surname, hash) VALUES(:email, :name, :surname, :hash)",
            email=request.form.get("email"),
            name=request.form.get("name"),
            surname=request.form.get("surname"),
            hash=hash)

        # Automatically log in the new user
        session["user_id"] = new_user
        session["role"] = "User"

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login """

    if request.method == "POST":

        # Query database for email
        rows = db.execute("SELECT id, email, hash, role FROM users WHERE email = :email",
            email=request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["role"] = rows[0]["role"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """ Logout """

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)