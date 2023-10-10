import os

from flask import Flask, redirect, session, render_template, flash
from forms import RegisterForm, LoginForm, CSRFProtectForm
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///notes"
)

connect_db(app)
db.create_all()

USERNAME = "username"

#TODO: Change redirect_to_register to homepage
@app.get("/")
def redirect_to_register():
    """Redirect to register page"""

    return redirect("/register")

#TODO: for register + login, if logged in redirect to their own page, make this tops
#Redirect with session[USERNAME]
@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Register a user to db, re-render form on invalid input
    If valid input, redirect to user profile page
    """

    form = RegisterForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        new_user = User.register(**data)

        db.session.add(new_user)
        db.session.commit()

        session[USERNAME] = new_user.username

        return redirect(f"/users/{new_user.username}")

    else:
        return render_template("user_register_form.html", form=form)

#TODO: Make URL for in the redirects 
@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Show/process login form.
    Ensures user authentication and then directs to user's profile
    """

    form = LoginForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        user = User.authenticate(**data)

        if user:
            session[USERNAME] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Bad name/password"]

    return render_template("user_login_form.html", form=form)


@app.get("/users/<username>")
def user_profile(username):
    """Show user profile"""

    if USERNAME not in session or session[USERNAME] != username:
        raise Unauthorized()
        # flash("You don't have access :(")
        # return redirect("/login")

    user = User.query.get_or_404(username)
    form = CSRFProtectForm()

    return render_template("user_profile.html", user=user, form=form)


@app.post("/logout")
def user_logout():
    """Logout user"""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop(USERNAME, None)
    else:
        raise Unauthorized()

    return redirect("/")
