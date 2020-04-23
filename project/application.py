import time
import re
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, login_admin_required, login_accepted_required, login_denied_prohibited, apology, eur, validate_iban



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

# Custom filter
app.jinja_env.filters["eur"] = eur

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")



""" Website """

@app.route("/")
def index():

    try:
        if session["role"] == "Admin":
            return redirect('/dashboard')
        else:
            return redirect('/finance')
    except:
        return redirect('/login')


@app.route("/finance", methods=["GET", "POST"])
@login_required
@login_accepted_required
def finance():
    """ Finance Form list """

    if request.method == "POST":

        # create a new form
        if request.form.get("data") == "create_form":

            # query default form information
            info = db.execute("SELECT name_director, name_accountant FROM Settings ORDER BY id desc LIMIT 1")[0]

            # insert new form
            finance = db.execute("INSERT INTO Finance (user_id, status, name_director, name_accountant) VALUES(:user_id, :status, :name_director, :name_accountant)",
                user_id=session["user_id"],
                status="Draft",
                name_director=info["name_director"],
                name_accountant=info["name_accountant"])

            if not finance:
                return jsonify(form=False, text='Failed to insert form into the database!')

            return jsonify(form=True, link=finance)

    else:

        finances = db.execute("""
            SELECT f.id,
                case when f.date is null then '-' else f.date end as date,
                case when f.number is null then '-' else f.number end as number,
                f.status,
                count(t.id) as count,
                case when sum(t.amount) is null then 0 else sum(t.amount) end as total_amount,
                case when sum(t.paid_amount) is null or sum(t.paid_amount) = -0.01 then 0 else sum(t.paid_amount) end as total_paid_amount
            FROM Finance f
            LEFT JOIN Transactions t ON t.finance_id = f.id
            WHERE f.user_id = :user_id
            GROUP BY f.id, f.date, f.number, f.status
            ORDER BY f.date""",
            user_id=session["user_id"])

        return render_template("finance.html", finances=finances)


@app.route("/finance/<finance_id>", methods=["GET", "POST"])
@login_required
@login_accepted_required
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

                # get values for the bank accounts
                bank = db.execute("SELECT bank_name, bank_code, bank_iban FROM Bank WHERE id=:bank_id", bank_id=request.form.get("bank_id"))[0]

                finance = db.execute("UPDATE Finance SET date=:date, text=:text, paid_bank_name=:paid_bank_name, paid_bank_code=:paid_bank_code, paid_bank_iban=:paid_bank_iban WHERE id=:finance_id",
                    date=request.form.get("date"),
                    text=request.form.get("text"),
                    paid_bank_name=bank["bank_name"],
                    paid_bank_code=bank["bank_code"],
                    paid_bank_iban=bank["bank_iban"],
                    finance_id=finance_id)

            return redirect("/finance/" + str(finance_id))

        else:

            # SELECT for Finance Form information and list of Transactions
            finance = db.execute("""
                SELECT
                    f.id,
                    f.user_id,
                    u.name || ' ' || u.surname as username,
                    case when u.personal_code is null or u.personal_code = '' then 'xxxxxx-xxxxx' else u.personal_code end as personal_code,
                    f.date,
                    case when f.number is null or f.number = '' then '-' else f.number end as number,
                    f.status,
                    case when f.text is null then '' else f.text end as text,
                    f.name_director,
                    f.name_accountant,
                    f.paid_bank_name,
                    f.paid_bank_iban
                FROM Finance f
                LEFT JOIN Users u ON u.id = f.user_id
                WHERE f.id=:id""",
                id=finance_id)
            transactions = db.execute("""
                SELECT
                    id,
                    status,
                    case when date is null or date = '' then '-' else date end as date,
                    case when partner is null or partner = '' then '-' else partner end as partner,
                    case when document_type is null or document_type = '' then '-' else document_type end as document_type,
                    case when document_no is null or document_no = '' then '-' else document_no end as document_no,
                    case when expense is null or expense = '' then '-' else expense end as expense,
                    amount,
                    case when paid_amount is null or paid_amount = -0.01 then 0 else paid_amount end as paid_amount
                FROM Transactions
                WHERE finance_id=:finance_id""",
                finance_id=finance_id)
            info = db.execute("SELECT count(id) as count, sum(amount) as total_amount, case when sum(paid_amount) < 0 then 0 else sum(paid_amount) end as total_paid_amount FROM Transactions WHERE finance_id=:finance_id", finance_id=finance_id)

            # check if the user has personal code and bank account data in settings
            banks = db.execute("SELECT id, bank_name, bank_iban, active FROM Bank WHERE user_id=:user_id ORDER BY active desc, createdate desc", user_id=session["user_id"])

            # check for user errors
            errors = []

            if finance[0]['date'] == None or finance[0]['date'] == 'None' or finance[0]['date'] == '':
                errors.append('Please input valid date')

            if finance[0]['text'] == None or finance[0]['text'] == 'None' or finance[0]['text'] == '':
                errors.append('Please input description text')

            valid_trans_count = 0
            for transaction in transactions:
                if transaction["status"] == 'New':
                    valid_trans_count += 1

            if valid_trans_count == 0:
                errors.append('Please add at least one valid transaction')

            if finance[0]['personal_code'] == None or finance[0]['personal_code'] == 'None' or finance[0]['personal_code'] == '' or finance[0]['personal_code'] == 'xxxxxx-xxxxx':
                errors.append('Please enter personal code in settings')

            if len(banks) == 0:
                errors.append('Please enter bank account information in settings')


            # check for admin errors
            admin_errors = []

            if finance[0]["status"] == "Review":
                if finance[0]['number'] == None or finance[0]['number'] == 'None' or finance[0]['number'] == '' or finance[0]['number'] == '-':
                    admin_errors.append('Set Number')

                valid_trans_count = 0
                for transaction in transactions:
                    if transaction["status"] == "Accepted" or transaction["status"] == "Denied":
                        valid_trans_count += 1

                if valid_trans_count == 0:
                    admin_errors.append('Review transactions')

            return render_template("finance_form.html", finance=finance[0], transactions=transactions, banks=banks, info=info[0], errors=errors, admin_errors=admin_errors)

    else:
        return redirect('/')


@app.route("/finance/create_transaction", methods=["POST"])
@login_required
@login_accepted_required
def finance_transaction_new():
    """ Create New Transaction inside Finance Form """

    finance_id=request.form.get("financeId")

    # check if the user can access this portion
    user_id = db.execute("SELECT user_id FROM Finance WHERE id=:finance_id", finance_id=finance_id)

    if session["user_id"] == user_id[0]["user_id"] or session["role"] == 'Admin':

        # add new transaction to the respective finance form
        transaction = db.execute("INSERT INTO Transactions (finance_id, status) VALUES(:finance_id, :status)",
            finance_id=finance_id,
            status="Draft")

        if not transaction:
            return jsonify(insert=False, text='Failed to insert transaction into the database!')

        return jsonify(insert=True, link=transaction)

    else:
        return redirect('/')


@app.route("/finance/user_status_change", methods=["POST"])
@login_required
@login_accepted_required
def finance_status_change():

    finance_id = request.form.get("financeId")

    # check if the user can access this portion
    user_id = db.execute("SELECT user_id FROM Finance WHERE id=:finance_id", finance_id=finance_id)

    if session["user_id"] == user_id[0]["user_id"] or session["role"] == 'Admin':

        change = request.form.get("change")

        # on submit
        if change == 'submit':

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

        # on delete
        if change == 'delete':

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

    else:
        return redirect('/')


@app.route("/finance/admin_status_change", methods=["POST"])
@login_required
@login_accepted_required
@login_admin_required
def finance_admin_status_change():

    finance_id = request.form.get("financeId")
    change = request.form.get("change")

    # on assign
    if change == 'assign':

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

    # on status change
    if change == 'status':

        status = request.form.get("status")
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
@login_accepted_required
def transaction(finance_id, transaction_id):
    """ Individual Finance transactions """

    # check if the user can access this portion
    user_id = db.execute("SELECT user_id FROM Finance WHERE id=:finance_id", finance_id=finance_id)

    if session["user_id"] == user_id[0]["user_id"] or session["role"] == 'Admin':

        if request.method == "POST":

            if session["role"] == "Admin":
                paid_amount = request.form.get("paid_amount")

                amount = db.execute("SELECT amount FROM Transactions WHERE id=:transaction_id", transaction_id=transaction_id)[0]["amount"]
                if float(paid_amount) > float(amount):
                    return apology("accepted amount cannot be larger than original amount", 400)

                # UPDATE for Transaction information
                transaction = db.execute("UPDATE Transactions SET date=:date, partner=:partner, expense=:expense, document_type=:document_type, document_no=:document_no, amount=:amount, paid_amount=:paid_amount WHERE id=:transaction_id",
                    date=request.form.get("date"),
                    partner=request.form.get("partner"),
                    expense=request.form.get("expense"),
                    document_type=request.form.get("document_type"),
                    document_no=request.form.get("document_no"),
                    amount=request.form.get("amount"),
                    paid_amount=paid_amount,
                    transaction_id=transaction_id)

                if not transaction:
                    return apology("transaction update failed", 400)

            else:

                # UPDATE for Transaction information
                transaction = db.execute("UPDATE Transactions SET date=:date, partner=:partner, expense=:expense, document_type=:document_type, document_no=:document_no, amount=:amount WHERE id=:transaction_id",
                    date=request.form.get("date"),
                    partner=request.form.get("partner"),
                    expense=request.form.get("expense"),
                    document_type=request.form.get("document_type"),
                    document_no=request.form.get("document_no"),
                    amount=request.form.get("amount"),
                    transaction_id=transaction_id)

                if not transaction:
                    return apology("transaction update failed", 400)

            return redirect("/finance/" + str(finance_id) + '/' + str(transaction_id))

        else:

            # SELECT for finance transaction information
            transaction = db.execute("""
                SELECT
                    t.id,
                    t.finance_id,
                    t.status,
                    t.date,
                    case when t.partner is null then '' else t.partner end as partner,
                    case when t.document_type is null then '' else t.document_type end as document_type,
                    case when t.document_no is null then '' else t.document_no end as document_no,
                    case when t.expense is null then '' else t.expense end as expense,
                    t.amount,
                    t.paid_amount,
                    f.status as fin_status
                FROM Transactions t
                LEFT JOIN Finance f ON f.id = t.finance_id
                WHERE t.id = :id""",
                id=transaction_id)

            document_types = db.execute("SELECT document_types FROM Settings ORDER BY id desc LIMIT 1")[0]
            document_types = document_types["document_types"].split(',')

            # check for errors
            errors = []

            if transaction[0]["date"] is None or transaction[0]["date"] == 'None' or transaction[0]["date"] == '':
                errors.append('Please input valid date')

            if transaction[0]["partner"] is None or transaction[0]["partner"] == 'None' or transaction[0]["partner"] == '':
                errors.append('Please input partner company name')

            if transaction[0]["document_type"] is None or transaction[0]["document_type"] == 'None' or transaction[0]["document_type"] == '':
                errors.append('Please input document type')

            if transaction[0]["document_no"] is None or transaction[0]["document_no"] == 'None' or transaction[0]["document_no"] == '':
                errors.append('Please input document number')

            if transaction[0]["expense"] is None or transaction[0]["expense"] == 'None' or transaction[0]["expense"] == '':
                errors.append('Please input expense description')

            if transaction[0]["amount"] == 0:
                errors.append('Please input expense amount')

            # check for admin errors
            admin_errors = []

            if transaction[0]["status"] == "Review":
                if transaction[0]["paid_amount"] == -0.01:
                    admin_errors.append('Input accepted value')

            return render_template("finance_transaction.html", transaction=transaction[0], document_types=document_types, errors=errors, admin_errors=admin_errors)

    else:
        return redirect('/')


@app.route("/transaction/user_status_change", methods=["POST"])
@login_required
@login_accepted_required
def transaction_status_change():

    finance_id = request.form.get("financeId")

    # check if the user can access this portion
    user_id = db.execute("SELECT user_id FROM Finance WHERE id=:finance_id", finance_id=finance_id)

    if session["user_id"] == user_id[0]["user_id"] or session["role"] == 'Admin':

        transaction_id = request.form.get("transactionId")
        change = request.form.get("change")

        # on submit
        if change == 'submit':

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

        # on delete
        if change == 'delete':

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

    else:
        return redirect('/')


@app.route("/transaction/admin_status_change", methods=["POST"])
@login_required
@login_accepted_required
@login_admin_required
def transaction_admin_status_change():

    finance_id = request.form.get("financeId")
    transaction_id =  request.form.get("transactionId")
    status = request.form.get("status")

    valid_statuses = ['Accepted', 'Denied']

    # validation for input
    if any(status for valid_status in valid_statuses):

        # make sure form is in review stage
        form_check = db.execute("SELECT status FROM Finance WHERE id = :finance_id", finance_id=finance_id)
        if form_check[0]["status"] != "Review":
            return jsonify(status=False, text="Form must be in Review status!")

        # make sure previous status is under review or at least accepted/denied
        status_check = db.execute("SELECT status, amount FROM Transactions WHERE id=:transaction_id", transaction_id=transaction_id)
        if status_check[0]["status"] == "Review" or status_check[0]["status"] == "Accepted" or status_check[0]["status"] == "Denied":

            # UPDATE database
            status_change = db.execute("UPDATE Transactions SET status = :status WHERE id=:transaction_id",
                            status = status,
                            transaction_id = transaction_id)

            # if accepted UPDATE paid_amount
            if status == "Accepted":
                db.execute("UPDATE Transactions SET paid_amount=:paid_amount WHERE id=:transaction_id",
                    paid_amount=status_check[0]["amount"],
                    transaction_id = transaction_id)

            if not status_change:
                return jsonify(status=False, text="Database UPDATE failed!")
            return jsonify(status=True)

        else:
            return jsonify(status=False, text="Transaction status must be in Review, Accepted or Denied!")

    else:
        return jsonify(status=False, text="Invalid input!")


@app.route("/dashboard", methods=["GET"])
@login_required
@login_accepted_required
@login_admin_required
def dashboard():
    """ Admin Finance Form board"""

    dashboards = db.execute("""
        SELECT
            f.id,
            u.name || ' ' || u.surname as user,
            case when f.date is null then '-' else f.date end as date,
            case when f.number is null then '-' else f.number end as number,
            f.status,
            count(t.id) as count,
            case when sum(t.amount) is null then 0 else sum(t.amount) end as total_amount,
            case when sum(t.paid_amount) is null or sum(t.paid_amount) = -0.01 then 0 else sum(t.paid_amount) end as total_paid_amount
        FROM Finance f
        LEFT JOIN Transactions t ON t.finance_id = f.id
        LEFT JOIN Users u ON u.id = f.user_id
        GROUP BY f.id, u.name, u.surname, f.date, f.number, f.status
        ORDER BY f.date""")

    reviews = db.execute("""
        SELECT
            f.id,
            u.name || ' ' || u.surname as user,
            case when f.date is null then '-' else f.date end as date,
            case when f.number is null then '-' else f.number end as number,
            f.status,
            count(t.id) as count,
            case when sum(t.amount) is null then 0 else sum(t.amount) end as total_amount,
            case when sum(t.paid_amount) is null or sum(t.paid_amount) = -0.01 then 0 else sum(t.paid_amount) end as total_paid_amount
        FROM Finance f
        LEFT JOIN Transactions t ON t.finance_id = f.id
        LEFT JOIN Users u ON u.id = f.user_id
        WHERE f.status in ('Review', 'New', 'Accepted')
        GROUP BY f.id, u.name, u.surname, f.date, f.number, f.status
        ORDER BY f.date""")

    return render_template("dashboard.html", dashboards=dashboards, reviews=reviews)


@app.route("/settings", methods=["GET", "POST"])
@login_required
@login_denied_prohibited
def settings():
    """ Settings """

    # query for settings data
    info = db.execute("SELECT email, name, surname, personal_code FROM Users WHERE id = :id", id=session["user_id"])
    banks = db.execute("SELECT id, bank_name, bank_code, bank_iban, active FROM Bank WHERE user_id = :user_id", user_id=session["user_id"])

    if request.method == "POST":
        # implmenet validation

        # check if password change is required
        if request.form.get("password") is not '' or request.form.get("password_new_1") is not '' or request.form.get("password_new_2") is not '':
            # if password change is required - UPDATE everything

            # make sure email is valid
            if not bool(re.match(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$', request.form.get("email"))):
                return apology("incorrect email", 400)

            # make sure name/surname is valid
            if bool(re.match(r'[\s]', request.form.get("name"))) or bool(re.match(r'[\s]', request.form.get("surname"))):
                return apology("name or surname cannot contain whitespace", 400)

            if bool(re.match(r'[^a-zA-Z]', request.form.get("name"))) or bool(re.match(r'[^a-zA-Z]', request.form.get("surname"))):
                return apology("name or surname must contain only letters", 400)

            password_hash = db.execute("SELECT hash FROM Users WHERE id = :id", id = session["user_id"])

            # check if current pasword is correct
            if len(password_hash) != 1 or not check_password_hash(password_hash[0]["hash"], request.form.get("password")):
                return apology("invalid current password", 400)

            # make sure new password is valid
            if not request.form.get('password_new_1') == request.form.get('password_new_2'):
                return apology("both passwords must be the same", 400)

            if not len(request.form.get("password_new_1")) >= 8:
                return apology("password must be at least 8 characters long", 400)

            if not bool(re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', request.form.get("password_new_1"))):
                return apology("password must contain at least one character and one number", 400)

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
                return redirect('/settings')

            else:

                # make sure email is valid
                if not bool(re.match(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$', request.form.get("email"))):
                    return apology("incorrect email", 400)

                # make sure name/surname is valid
                if bool(re.match(r'[\s]', request.form.get("name"))) or bool(re.match(r'[\s]', request.form.get("surname"))):
                    return apology("name or surname cannot contain whitespace", 400)

                if bool(re.match(r'[^a-zA-Z]', request.form.get("name"))) or bool(re.match(r'[^a-zA-Z]', request.form.get("surname"))):
                    return apology("name or surname must contain only letters", 400)

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

        return render_template("settings.html", info=info, banks=banks)


@app.route("/bank_add", methods=["POST"])
@login_required
def bank_add():
    """ Add Bank Account """

    # get list of already existing user banks
    banks = db.execute("SELECT bank_iban FROM Bank WHERE user_id=:user_id", user_id=session["user_id"])

    # validate IBAN
    iban = validate_iban(request.form.get("bank_iban"))
    if not iban["valid"]:
        print(iban["error"])
        return jsonify(bank=False, text=iban["error"])

    default = request.form.get("active")

    # change default if requested
    if default == 'true':
        db.execute("UPDATE Bank SET active='false' WHERE user_id=:user_id", user_id=session["user_id"])

    # if default not requested but it is the only bank account - make it default
    elif default == 'false' and len(banks) == 0:
        default = 'true'

    # insert bank account into the database
    bank = db.execute("INSERT INTO Bank (user_id, bank_name, bank_code, bank_iban, active) VALUES (:user_id, :bank_name, :bank_code, :bank_iban, :active)",
        user_id=session["user_id"],
        bank_name=request.form.get("bank_name"),
        bank_code=request.form.get("bank_code"),
        bank_iban=iban["iban"],
        active=default)

    if not bank:
        return jsonify(bank=False, text="Database INSERT failed!")

    return jsonify(bank=True)


@app.route("/bank_delete", methods=["POST"])
@login_required
def bank_delete():
    """ Delete Bank Account """

    # check if the user can access this portion
    user_id = db.execute("SELECT user_id FROM Bank WHERE id=:bank_id", bank_id=request.form.get("bank_id"))

    if session["user_id"] == user_id[0]["user_id"] or session["role"] == 'Admin':

        # check if the default bank account has to be changed
        if db.execute("SELECT active FROM Bank WHERE id=:bank_id", bank_id=request.form.get("bank_id"))[0]["active"] == "true":

            # if so, change it to the last previous bank account (if such exists)
            bank = db.execute("SELECT id, createdate, active FROM Bank WHERE user_id=:user_id ORDER BY createdate desc LIMIT 1", user_id=session["user_id"])
            if bank:
                db.execute("UPDATE Bank SET active='true' WHERE id=:bank_id", bank_id=bank[0]["id"])

        # delete bank account
        delete = db.execute("DELETE FROM Bank WHERE id=:bank_id", bank_id=request.form.get("bank_id"))

        if not delete:
            return jsonify(delete=False, text="Database DELETE failed!")
        return jsonify(delete=True)


@app.route("/bank_default", methods=["POST"])
@login_required
def bank_default():
    """ Set Default Bank Account """

    # check if the user can access this portion
    user_id = db.execute("SELECT user_id FROM Bank WHERE id=:bank_id", bank_id=request.form.get("bank_id"))

    if session["user_id"] == user_id[0]["user_id"] or session["role"] == 'Admin':

        # change default bank account
        default = db.execute("UPDATE Bank SET active='true' WHERE id=:bank_id", bank_id=request.form.get("bank_id"))

        if not default:
            return jsonify(default=False, text="Database UPDATE failed!")

        # change other bank account status
        default = db.execute("UPDATE Bank SET active='false' WHERE user_id=:user_id and id!=:bank_id",
            user_id=session["user_id"],
            bank_id=request.form.get("bank_id"))

        if not default:
            return jsonify(default=False, text="Second Database UPDATE failed!")
        return jsonify(default=True)


@app.route("/admin_settings", methods=["GET", "POST"])
@login_required
@login_admin_required
def admin_settings():
    """ Admin Settings """

    if request.method == "POST":

        # SANITIZE INPUTS
        db.execute("INSERT INTO Settings (name_director, name_accountant, document_types) VALUES (:name_director, :name_accountant, :document_types)",
            name_director=request.form.get("name_director"),
            name_accountant=request.form.get("name_accountant"),
            document_types=request.form.get("document_types"))

        return redirect('/admin_settings')

    else:

        info = db.execute("SELECT name_director, name_accountant, document_types FROM Settings ORDER BY id desc LIMIT 1")
        return render_template("settings_admin.html", info=info[0])


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register """

    if request.method == "POST":

        # make sure email is valid
        if not bool(re.match(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$', request.form.get("email"))):
            return apology("incorrect email", 400)

        # make sure name/surname is valid
        if bool(re.match(r'[\s]', request.form.get("name"))) or bool(re.match(r'[\s]', request.form.get("surname"))):
            return apology("name or surname cannot contain whitespace", 400)

        if bool(re.match(r'[^a-zA-Z]', request.form.get("name"))) or bool(re.match(r'[^a-zA-Z]', request.form.get("surname"))):
            return apology("name or surname must contain only letters", 400)

        # make sure password is valid
        if not request.form.get('password') == request.form.get('confirmpassword'):
            return apology("both passwords must be the same", 400)

        if not len(request.form.get("password")) >= 8:
            return apology("password must be at least 8 characters long", 400)

        if not bool(re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', request.form.get("password"))):
            return apology("password must contain at least one character and one number", 400)

        # create hash from password
        hash = generate_password_hash(request.form.get("password"))

        # insert new user into database
        new_user = db.execute("INSERT INTO Users (email, name, surname, hash) VALUES(:email, :name, :surname, :hash)",
            email=request.form.get("email"),
            name=request.form.get("name"),
            surname=request.form.get("surname"),
            hash=hash)

        if not new_user:
            return apology("user with this email already exists!", 400)

        # automatically log in the new user
        session["user_id"] = new_user
        session["role"] = "User"
        session["status"] = "New"

        return redirect("/register_status")

    else:
        return render_template("register.html")


@app.route("/register_email_validation", methods=["GET"])
def register_email_validation():

    email = request.args.get("email")
    available = db.execute("SELECT email FROM Users WHERE email=:email", email=email)
    if not available:
        return jsonify(True)
    return jsonify('This email already exists')


@app.route("/registration", methods=["GET", "POST"])
@login_required
@login_accepted_required
@login_admin_required
def registration():
    """ Registration whitelist """

    if request.method == "POST":

        user_id = request.form.get("user_id")
        status = request.form.get("status")

        # make sure correct user status is submitted
        if status == 'Accepted' or status == 'Denied':

            # update user status
            user = db.execute("UPDATE Users SET status=:status, status_changed=:status_changed, status_changed_by=:status_changed_by WHERE id=:user_id",
                status=status,
                status_changed=datetime.today().strftime('%Y-%m-%d'),
                status_changed_by=session["user_id"],
                user_id=user_id)

            if not user:
                return jsonify(status=False, text="Database UPDATE failed!")
            return jsonify(status=True)

    else:

        users = db.execute("SELECT id, createdate, email, name || ' ' || surname as name, status FROM Users WHERE role != 'Admin' ORDER BY createdate desc")
        return render_template("registration.html", users=users)


@app.route("/register_status", methods=["GET"])
@login_required
def reg_status():
    """ Registration whitelist status """

    return render_template("register_status.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login """

    if request.method == "POST":

        # query database for email
        login = db.execute("SELECT id, email, hash, role, status FROM Users WHERE email = :email",
            email=request.form.get("email"))

        # ensure email exists and password is correct
        if len(login) != 1 or not check_password_hash(login[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # remember which user has logged in
        session["user_id"] = login[0]["id"]
        session["role"] = login[0]["role"]
        session["status"] = login[0]["status"]

        # redirect user to home page
        if session["status"] == 'Accepted':
            return redirect("/")

        return redirect("/register_status")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """ Logout """

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect("/login")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)