import cs50
import csv
import re

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    """"Getting Values"""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    password = request.form.get('password')
    country = request.form.get('country')
    gender = request.form.get('gender')

    # checks if username already exists
    with open("survey.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[2] == username:
                return render_template("error.html", message="Username already exists!")

    # Validates password
    if len(password) < 8:
        return render_template("error.html", message="Password is too short!")
    elif len(password) > 20:
        return render_template("error.html", message="Password is too long!")

    # write data to csv
    with open("survey.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow((first_name, last_name, username, password, country, gender))

    return redirect('/sheet')


@app.route("/sheet", methods=["GET"])
def get_sheet():
    """"Show data"""
    with open('survey.csv', 'r') as file:
        reader = csv.reader(file)
        table_rows = list(reader)

        # Checks if DB is empty
        if len(table_rows) == 0:
            return render_template("error.html", message="No data to show")

    return render_template("sheet.html", table_rows=table_rows)