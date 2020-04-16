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
    return redirect('/finance')


@app.route("/finance")
@login_required
def finance():
    """ Finance Form list """

    # SELECT for the list of finance forms in main 'Finance' page
    finances = db.execute("SELECT id, date, number, status, name_director, name_accountant FROM Finance WHERE user_id = :user_id ORDER BY date",
        user_id=session["user_id"])

    return render_template("finance.html", finances=finances)


@app.route("/create_form")
@login_required
def finance_form_new():
    """ Create new Finance Form """

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
    """ Individual Finance Form """

    # check if the user can access this portion
    user_id = db.execute("SELECT user_id FROM Finance WHERE id=:finance_id", finance_id=finance_id)

    if session["user_id"] == user_id[0]["user_id"] or session["role"] == 'Admin':

        if request.method == "POST":

            # checking if the user is Admin for full form UPDATE
            if session["role"] == 'Admin':

                # UPDATE for Finance Form information
                finance = db.execute("UPDATE Finance SET number=:number, date=:date, text=:text, name_director=:name_director, name_accountant=:name_accountant WHERE id=:finance_id",
                        number=request.form.get("number"),
                        date=request.form.get("date"),
                        text=request.form.get("text"),
                        name_director=request.form.get("name_director"),
                        name_accountant=request.form.get("name_accountant"),
                        finance_id=finance_id)

            # if user is not Admin
            else:

                finance = db.execute("UPDATE Finance SET date=:date, text=:text WHERE id=:finance_id",
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

            return render_template("finance_form.html", finance=finance, transactions=transactions)

    else:
        redirect('/')


@app.route("/finance/<finance_id>/create_transaction", methods=["GET"])
@login_required
def finance_transaction_new(finance_id):
    """ Create New Transaction inside Finance Form """

    # TODO implement anti-spamming control which checks DB for the last form entry

    # INSERT for blank Transaction in the database
    transaction = db.execute("INSERT INTO Transactions (finance_id, status) VALUES(:finance_id, :status)",
                finance_id=finance_id,
                status="Draft")

    if not transaction:
        return jsonify(False)

    return jsonify(True)


@app.route("/finance/<finance_id>/submit", methods=["GET"])
@login_required
def finance_submit(finance_id):
    """ Submit Form for approval """

    # check if the form is already submitted
    status = db.execute("SELECT status FROM Finance WHERE id=:finance_id", finance_id = finance_id)

    if status[0]["status"] == 'New':

        # form is already submitted - unsubmit
        unsubmit = db.execute("UPDATE Finance SET status = :status WHERE id=:finance_id",
            status = "Draft",
            finance_id = finance_id)

        if not unsubmit:
            return jsonify(submit=False, text="Database UPDATE failed")
        return jsonify(submit=True)

    elif status[0]["status"] == "Review" or status[0]["status"] == "Accepted" or status[0]["status"] == "Denied" or status[0]["status"] == "Paid":

        # form is in a later status stage, therefore ineligible
        return jsonify(submit=False, text="You cannot submit this form because it is already Submitted!")

    else:

        # form is not submited
        # check if all transactions are submited

        transactions = db.execute("SELECT status FROM Transactions WHERE finance_id=:finance_id", finance_id = finance_id)
        for transaction in transactions:
            if transaction["status"] != "New":
                return jsonify(submit=False, text="You cannot submit the Form because there are unfinished transactions!")

        # submit form
        submit = db.execute("UPDATE Finance SET status = :status WHERE id=:finance_id",
                status = "New",
                finance_id = finance_id)

        if not submit:
            return jsonify(submit=False, text="Database UPDATE failed")
        return jsonify(submit=True)


@app.route("/finance/<finance_id>/delete", methods=["GET"])
@login_required
def finance_delete(finance_id):
    """ Delete Form """

    form = db.execute("SELECT user_id, status FROM Finance WHERE id=:finance_id", finance_id=finance_id)

    # cross-user validation
    if session["role"] != "Admin":
        if session["user_id"] != form[0]["user_id"]:
            redirect('/')


    if session["role"] != "Admin":

        # if the form is in Draft and New state it can be deleted by anyone
        if form[0]["status"] == "Draft" or form[0]["status"] == "New":

            delete = db.execute("DELETE FROM Finance WHERE id=:finance_id", finance_id=finance_id)
            db.execute("DELETE FROM Transactions WHERE finance_id=:finance_id", finance_id=finance_id)

            if not delete:
                return jsonify(delete=False, text="Delete failed - Please contact Admin!")
            return jsonify(delete=True)

        else:
            return jsonify(delete=False, text="You don't have the required permission to delete this Form!")

    elif session["role"] == "Admin":

        # admins have permission to delete any form
        delete = db.execute("DELETE FROM Finance WHERE id=:finance_id", finance_id=finance_id)
        db.execute("DELETE FROM Transactions WHERE finance_id=:finance_id", finance_id=finance_id)

        if not delete:
            return jsonify(delete=False, text="Delete failed - Please contact Admin!")
        return jsonify(delete=True)


@app.route("/finance/<finance_id>/status/assign", methods=["GET"])
@login_required
@login_admin_required
def finance_assign(finance_id):
    """ Assign Form to Admin for Approval """

    # check if there are any transactions before review
    transactions = db.execute("SELECT id FROM Transactions WHERE finance_id=:finance_id", finance_id=finance_id)
    if not transactions:
        return jsonify(assign=False, text="Cannot assign a form with no Transactions!")

    # assign form to an admin for approval
    assign = db.execute("UPDATE Finance SET review_id = :review_id, status = :status WHERE id=:finance_id",
                review_id = session["user_id"],
                status = "Review",
                finance_id = finance_id)

    assign_transactions = db.execute("UPDATE Transactions SET review_id = :review_id, status = :status WHERE finance_id=:finance_id",
                review_id = session["user_id"],
                status = "Review",
                finance_id = finance_id)

    if not assign or not assign_transactions:
        return jsonify(assign=False, text="Database UPDATE failed!")
    return jsonify(assign=True)


@app.route("/finance/<finance_id>/status/<status>", methods=["GET"])
@login_required
@login_admin_required
def finance_status(finance_id, status):
    """ Form status change Workflow """

    if status == "Accepted" or status == "Denied":

        # make sure that form is under review, accepted or denied
        status_change = db.execute("SELECT status FROM Finance WHERE id=:finance_id", finance_id=finance_id)
        if status_change[0]["status"] != "Review" and status_change[0]["status"] != "Accepted" and status_change[0]["status"] != "Denied":
            return jsonify(status=False, text="Form is not under Review, Accepted or Denied!")

        # make sure that all transactions are accepted or denied
        transactions = db.execute("SELECT status FROM Transactions WHERE finance_id=:finance_id", finance_id = finance_id)
        for transaction in transactions:
            if transaction["status"] != "Accepted" and transaction["status"] != "Denied":
                return jsonify(status=False, text="All Transactions are not either Accepted or Denied!")

        accepted = 0
        for transaction in transactions:
            if transaction["status"] == "Accepted":
                accepted += 1

        # make sure if the form is accepted then at least one transaction is also accepted
        if status == "Accepted" and accepted < 1:
            return jsonify(status=False, text="Cannot Accept if there are no Accepted Transactions!")

        #        or if the form is denied then all transactions should be denied too
        if status == "Denied" and accepted > 0:
            return jsonify(status=False, text="Cannot Deny if there are no Denied Transactions!")

        # UPDATE database
        update = db.execute("UPDATE Finance SET status = :status WHERE id=:finance_id",
                        status = status,
                        finance_id = finance_id)

        if not update:
            return jsonify(status=False, text="Database UPDATE failed!")
        return jsonify(status=True)

    elif status == "Paid":

        # make sure that form is under review, accepted or denied
        status_change = db.execute("SELECT status FROM Finance WHERE id=:finance_id", finance_id=finance_id)
        if status_change[0]["status"] != "Review" and status_change[0]["status"] != "Accepted" and status_change[0]["status"] != "Denied":
            return jsonify(status=False, text="Form is not under Review, Accepted or Denied!")

        # UPDATE database
        update = db.execute("UPDATE Finance SET status = :status WHERE id=:finance_id",
                    status = status,
                    finance_id = finance_id)

        if not update:
            return jsonify(status=False, text="Database UPDATE failed!")

        # UPDATE accepted transactions

        update = db.execute("UPDATE Transactions SET status = :status WHERE finance_id=:finance_id and status='Accepted'",
            status=status,
            finance_id=finance_id)

        if not update:
            return jsonify(status=False, text="Database UPDATE failed!")

        return jsonify(status=True)

    else:
        return redirect("/")


@app.route("/finance/<finance_id>/<transaction_id>", methods=["GET", "POST"])
@login_required
def transaction(finance_id, transaction_id):
    """ Individual Finance transactions """

    if request.method == "POST":

        print(request.form.get("date"), request.form.get("partner"), request.form.get("expense"), request.form.get("amount"))

        # UPDATE for Transaction information
        transaction = db.execute("UPDATE Transactions SET date=:date, partner=:partner, expense=:expense, amount=:amount WHERE id=:transaction_id",
                    date=request.form.get("date"),
                    partner=request.form.get("partner"),
                    expense=request.form.get("expense"),
                    amount=request.form.get("amount"),
                    transaction_id=transaction_id)

        if not transaction:
            return apology("transaction update failed", 400)

        return redirect("/finance/" + str(finance_id) + '/' + str(transaction_id))

    else:

        # SELECT for finance transaction information
        transaction = db.execute("SELECT id, finance_id, status, date, partner, expense, amount FROM Transactions WHERE id = :id",
            id=transaction_id)

        return render_template("finance_transaction.html", transaction=transaction)


@app.route("/finance/<finance_id>/<transaction_id>/submit", methods=["GET"])
@login_required
def transaction_submit(finance_id, transaction_id):
    """ Submit Transaction for Review """

    # check if eligible for submission
    transaction = db.execute("SELECT date, partner, expense, amount FROM Transactions WHERE id=:transaction_id", transaction_id=transaction_id)
    if (transaction[0]["date"] is None or transaction[0]["date"] == '' or transaction[0]["date"] == 'None' or transaction[0]["partner"] is None or transaction[0]["partner"] == '' or transaction[0]["partner"] == 'None' or
        transaction[0]["expense"] is None or transaction[0]["expense"] == '' or transaction[0]["expense"] == 'None' or transaction[0]["amount"] is None or transaction[0]["amount"] == '' or transaction[0]["amount"] == 'None'):
        return jsonify(submit=False, text="Transaction cannot be submitted as it is not finished!")

    # check if the transaction is already submitted
    status = db.execute("SELECT status FROM Transactions WHERE id=:transaction_id", transaction_id = transaction_id)

    if status[0]["status"] == 'New':

        # transaction is already submitted - unsubmit
        unsubmit = db.execute("UPDATE Transactions SET status = :status WHERE id=:transaction_id",
            status = "Draft",
            transaction_id = transaction_id)

        if not unsubmit:
            return jsonify(submit=False, text="Database UPDATE failed!")
        return jsonify(submit=True)

    else:

        # transaction is not submited - submit
        submit = db.execute("UPDATE Transactions SET status = :status WHERE id=:transaction_id",
                status = "New",
                transaction_id = transaction_id)

        if not submit:
            return jsonify(submit=False, text="Database UPDATE failed!")
        return jsonify(submit=True)


@app.route("/finance/<finance_id>/<transaction_id>/delete", methods=["GET"])
@login_required
def transaction_delete(finance_id, transaction_id):
    """ Delete Transaction """

    transaction = db.execute("SELECT f.user_id, t.status FROM Finance f LEFT JOIN Transactions t ON t.finance_id = f.id WHERE t.id=:transaction_id", transaction_id=transaction_id)

    # cross-user validation
    if session["role"] != "Admin":
        if session["user_id"] != transaction[0]["user_id"]:
            redirect('/')


    if session["role"] != "Admin":

        # if the transaction is in Draft and New state it can be deleted by anyone
        if transaction[0]["status"] == "Draft" or transaction[0]["status"] == "New":

            delete = db.execute("DELETE FROM Transactions WHERE id=:transaction_id", transaction_id=transaction_id)

            if not delete:
                return jsonify(delete=False, text="Delete failed - Please contact Admin!")
            return jsonify(delete=True)

        else:
            return jsonify(delete=False, text="You don't have the required permission to delete this Transaction!")

    elif session["role"] == "Admin":

        # admins have permission to delete any form
        delete = db.execute("DELETE FROM Transactions WHERE id=:transaction_id", transaction_id=transaction_id)

        if not delete:
            return jsonify(delete=False, text="Delete failed - Please contact Admin!")
        return jsonify(delete=True)


@app.route("/finance/<finance_id>/<transaction_id>/status/<status>", methods=["GET"])
@login_required
@login_admin_required
def transaction_status(finance_id, transaction_id, status):
    """ Transaction status change Workflow """

    valid_statuses = ['Accepted', 'Denied']

    # validation for input
    if any(status for valid_status in valid_statuses):

        # make sure form is in review stage
        form_check = db.execute("SELECT status FROM Finance WHERE id = :finance_id", finance_id=finance_id)
        if form_check[0]["status"] != "Review":
            return jsonify(status=False, text="Form must be in Review status!")

        # make sure previous status is under review or at least accepted/denied
        status_check = db.execute("SELECT status FROM Transactions WHERE id=:transaction_id", transaction_id=transaction_id)
        if status_check[0]["status"] == "Review" or status_check[0]["status"] == "Accepted" or status_check[0]["status"] == "Denied":

            # UPDATE database
            status_change = db.execute("UPDATE Transactions SET status = :status WHERE id=:transaction_id",
                            status = status,
                            transaction_id = transaction_id)

            if not status_change:
                return jsonify(status=False, text="Database UPDATE failed!")
            return jsonify(status=True)

        else:
            return jsonify(status=False, text="Transaction status must be in Review, Accepted or Denied!")

    else:
        return jsonify(status=False, text="Invalid input!")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
@login_admin_required
def dashboard():
    """ Admin Finance Form board"""

    dashboards = db.execute("""SELECT f.id, u.name || ' ' || u.surname as user, f.date, f.number, f.status, f.name_director, f.name_accountant FROM Finance f
                               LEFT JOIN Users u ON u.id = f.user_id
                               ORDER BY date""")

    reviews = db.execute("""SELECT f.id, u.name || ' ' || u.surname as user, f.date, f.number, f.status, f.name_director, f.name_accountant FROM Finance f
                               LEFT JOIN Users u ON u.id = f.user_id
                               WHERE f.status in ('Review', 'New', 'Accepted')
                               ORDER BY date""")

    return render_template("dashboard.html", dashboards=dashboards, reviews=reviews)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """ Settings """

    # query for settings data
    info = db.execute("SELECT email, name, surname, personal_code FROM Users WHERE id = :id",
        id=session["user_id"])

    if request.method == "POST":
        # implmenet validation

        # check if password change is required
        if request.form.get("password") is not '' or request.form.get("password_new_1") is not '' or request.form.get("password_new_2") is not '':
            # if password change is required - UPDATE everything

            password_hash = db.execute("SELECT hash FROM Users WHERE id = :id", id = session["user_id"])

            # check if current pasword is correct
            if len(password_hash) != 1 or not check_password_hash(password_hash[0]["hash"], request.form.get("password")):
                return apology("invalid current password", 400)

            # check if the two new passwords are the same
            if request.form.get("password_new_1") != request.form.get("password_new_2"):
                return apology("confirmation password not matching", 400)

            # create new hash
            hash = generate_password_hash(request.form.get("password_new_1"))

            # update database
            update = db.execute("UPDATE Users SET email = :email, personal_code = :personal_code, name = :name, surname = :surname, hash = :hash WHERE id = :id",
                email = request.form.get("email"),
                personal_code = request.form.get("personal_code"),
                name = request.form.get("name"),
                surname = request.form.get("surname"),
                hash = hash,
                id = session["user_id"])

            if not update:
                return apology("update failed", 400)

            flash("Password and Settings changed")
            return redirect('/settings')

        else:
            # if password change is not required - UPDATE the rest of the fields if required
            if request.form.get("email") == info[0]["email"] and request.form.get("personal_code") == info[0]["personal_code"] and request.form.get("name") == info[0]["name"] and request.form.get("surname") == info[0]["surname"]:
                # no change - database UPDATE not required
                return render_template("settings.html", info=info)

            else:
                # change - database UPDATE required
                update = db.execute("UPDATE Users SET email = :email, personal_code = :personal_code, name = :name, surname = :surname WHERE id = :id",
                    email = request.form.get("email"),
                    personal_code = request.form.get("personal_code"),
                    name = request.form.get("name"),
                    surname = request.form.get("surname"),
                    id = session["user_id"])

                if not update:
                    return apology("Database UPDATE failed", 400)

                flash("Settings changed")
                return redirect('/settings')

    else:

        return render_template("settings.html", info=info)

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
        return render_template("settings_admin.html", info=info)

    else:
        # Query for info
        info = db.execute("SELECT name_director, name_accountant FROM Settings ORDER BY id desc LIMIT 1")
        return render_template("settings_admin.html", info=info)


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