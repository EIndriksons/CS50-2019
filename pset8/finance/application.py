import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, validate

# Configure application
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


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Query for user cash
    cash = float((db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"]))[0]["cash"])

    # Query for user stocks and share count
    stocks = db.execute("SELECT symbol, sum(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol",
                        user_id=session["user_id"])

    # Cash amount in stocks
    cash_stocks = 0

    # Lookup current stock information and add it to stocks
    for stock in stocks:
        result = lookup(stock['symbol'])
        stock['price'] = result['price']
        stock['name'] = result['name']
        cash_stocks += float(stock['price']) * int(stock['total_shares'])

    # Calculate total portfolio cash from cash + cash amount in stocks
    cash_portfolio = cash + cash_stocks

    return render_template("index.html", cash=cash, stocks=stocks, cash_portfolio=cash_portfolio)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # Ensure not empty
        if not (request.form.get("symbol") or request.form.get("shares")):
            return apology("please provide symbol and shares", 400)

        # Make sure variable is integer
        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("shares must be a posative integer", 400)

        if shares < 0:
            return apology("share count cannot be negative", 400)

        # Lookup stock symbol
        result = lookup(request.form.get("symbol"))

        # If API returns empty stock information - it must be wrong or empty
        if result == None:
            return apology("wrong quote", 400)

        # check user cash if he can buy the stocks
        if float((db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"]))[0]["cash"]) < float(result["price"]) * shares:
            return apology("not enough funds", 400)

        # ACCOUNTING: buy stock
        # Query to insert stock purchase into transactions
        db.execute("INSERT INTO transactions (type, user_id, symbol, shares, price) VALUES('Buy', :user_id, :symbol, :shares, :price)",
                   symbol=request.form.get("symbol"),
                   shares=shares,
                   price=round(float(result["price"]), 4),
                   user_id=session["user_id"])

        # Query to update user cash
        db.execute("UPDATE users SET cash = cash - :sum WHERE id = :user_id",
                   sum=round(float(result["price"]), 4) * shares,
                   user_id=session["user_id"])

        # Flash and return back to index page
        flash("Bought!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Check username lenght
    if len(request.args.get("username")) < 0:
        return jsonify(False)

    # Check if username already exists in the database
    elif len(db.execute("SELECT username FROM users WHERE username = :username", username=request.args.get("username"))) != 0:
        return jsonify(False)

    else:
        return jsonify(True)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get history from database
    transactions = db.execute("SELECT createdate, type, symbol, shares, price FROM transactions WHERE user_id = :user_id",
                              user_id=session["user_id"])

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        # Ensure anything was submitted
        if not request.form.get("symbol"):
            return apology("insert valid stock quote", 400)

        # Lookup quote
        result = lookup(request.form.get("symbol"))

        # If no result - show apology
        if result == None:
            return apology("wrong quote", 400)

        return render_template("quoted.html", result=result)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Get username (make sure not blank)
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Get password (make sure not blank)
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Get password2 (make sure not blank)
        # elif not request.form.get("password2"):                               !!! DISABLED FOR CHECK50
        #    return apology("must provide confirmation password", 400)          !!! DISABLED FOR CHECK50

        # Make sure passwords match
        # elif request.form.get("password") != request.form.get("password2"):   !!! DISABLED FOR CHECK50
        #    return apology("passwords must match", 400)                        !!! DISABLED FOR CHECK50

        # Make sure password is valid
        elif validate(request.form.get("password")):
            return apology("invalid password", 400)

        # Get confirmation (make sure form checked)
        elif not request.form.get("confirmation"):
            return apology("accept terms and conditions", 400)

        # Create hash from password
        hash = generate_password_hash(request.form.get("password"))

        # Insert user in database
        new_user = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                              username=request.form.get("username"),
                              hash=hash)

        # Check if the user is unique, if not -> apology
        if not new_user:
            return apology("username taken", 400)

        # Automatically log in the new user
        session["user_id"] = new_user

        flash("Registered!")
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        # Lookup stock information
        result = lookup(request.form.get("symbol"))

        # If API returns empty stock information - it must be wrong or empty
        if result == None:
            return apology("wrong quote", 400)

        # Making sure you own the number of shares you want to sell
        shares_owned = db.execute("SELECT sum(shares) as shares_owned FROM transactions WHERE symbol = :symbol and user_id = :user_id",
                                  symbol=request.form.get("symbol"),
                                  user_id=session["user_id"])

        if int(request.form.get("shares")) > int(shares_owned[0]["shares_owned"]):
            return apology("you cannot sell more than you own", 400)

        # Making sure share count is not negative
        if int(request.form.get("shares")) < 0:
            return apology("shares cannot be negative", 400)

        # Make sure variable is integer
        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("shares must be a posative integer", 400)

        # ACCOUNTING: sell stock
        # Query to insert stock purchase into transactions
        db.execute("INSERT INTO transactions (type, user_id, symbol, shares, price) VALUES('Sell', :user_id, :symbol, -:shares, :price)",
                   symbol=request.form.get("symbol"),
                   shares=int(request.form.get("shares")),
                   price=round(float(result["price"]), 4),
                   user_id=session["user_id"])

        # Query to update user cash
        db.execute("UPDATE users SET cash = cash + :sum WHERE id = :user_id",
                   sum=round(float(result["price"]), 4) * int(request.form.get("shares")),
                   user_id=session["user_id"])

        # Flash and return back to index page
        flash("Shares Sold!")
        return redirect("/")

    else:

        # Query for list of user shares to generate options
        stocks = db.execute("SELECT * FROM (SELECT symbol, sum(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol) symbol WHERE total_shares > 0",
                            user_id=session["user_id"])

        return render_template("sell.html", stocks=stocks)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user password"""

    if request.method == "POST":

        # Check validity of all fields
        if not request.form.get("current_password"):
            return apology("provide current password", 400)

        elif not request.form.get("new_password"):
            return apology("provide new password", 400)

        elif not request.form.get("new_password2"):
            return apology("must provide confirmation password", 400)

        elif request.form.get("new_password") != request.form.get("new_password2"):
            return apology("passwords must match", 400)

        # Make sure new password is valid
        elif validate(request.form.get("new_password")):
            return apology("invalid password", 400)

        # Authenticate user
        userdata = db.execute("SELECT * FROM users WHERE id = :user_id",
                              user_id=session["user_id"])

        if len(userdata) != 1 or not check_password_hash(userdata[0]["hash"], request.form.get("current_password")):
            # Clear session and log out the user
            session.clear()
            return apology("password is incorrect", 400)

        # Change password
        hash = generate_password_hash(request.form.get("new_password"))

        # Update password
        db.execute("UPDATE users SET hash = :hash WHERE id = :user_id",
                   user_id=session["user_id"],
                   hash=hash)

        # Flash and return back to index page
        flash("Password Changed!")
        return redirect("/")

    else:
        return render_template("change_password.html")


@app.route("/cash_add", methods=["GET", "POST"])
@login_required
def cash_add():
    """Add additional funds"""

    if request.method == "POST":

        # Check validity
        if not request.form.get("cash"):
            return apology("provide cash amount", 400)

        elif float(request.form.get("cash")) < 0:
            return apology("cash cannot be negative", 400)

        # Add cash to funds
        db.execute("UPDATE users SET cash = cash + :cash WHERE id = :user_id",
                   user_id=session["user_id"],
                   cash=round(float(request.form.get("cash")), 4))

        # Flash and return back to index page
        flash("Funds Added!")
        return redirect("/")

    else:
        return render_template("cash_add.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)