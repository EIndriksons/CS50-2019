from flask import redirect, render_template, request, session
from functools import wraps
from schwifty import IBAN


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def login_admin_required(f):
    """
    Decorate routes to require admin login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["role"] != 'Admin':
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def login_accepted_required(f):
    """
    Decorate routes to require accepted user profile.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["status"] != 'Accepted':
            return redirect("/register_status")
        return f(*args, **kwargs)
    return decorated_function


def login_denied_prohibited(f):
    """
    Decorate routes to require accepted user profile.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["status"] == 'Denied':
            return redirect("/register_status")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code):
    """Render message as an apology to user."""
    # def escape(s):
    #     """
    #     Escape special characters.
    #     https://github.com/jacebrowning/memegen#special-characters
    #     """
    #     for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
    #                      ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
    #         s = s.replace(old, new)
    #     return s
    return render_template("apology.html", top=code, bottom=message), code


def eur(value):
    """ Format value as EUR """
    return f"€{value:,.2f}"



def validate_iban(iban):
    """ Validate IBAN """
    try:
        return {'valid' : True, 'iban' : IBAN(iban).compact}
    except ValueError as e:
        return {'valid' : False, 'error' : str(e)}