import os

from flask import Flask, redirect, session, render_template, flash, url_for
from forms import RegisterForm, LoginForm, CSRFProtectForm, NoteForm
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Note

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///notes"
)

connect_db(app)
db.create_all()

USERNAME = "username"


@app.get("/")
def homepage():
    """Redirect to register page"""

    return redirect(url_for("register_user"))


@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Register a user to db, re-render form on invalid input
    If valid input, redirect to user profile page
    """

    if USERNAME in session:
        return redirect(url_for("user_profile", username=session[USERNAME]))

    form = RegisterForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        try:
            new_user = User.register(**data)
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            flash("Username already taken")
            return render_template("user_register_form.html", form=form)

        session[USERNAME] = new_user.username

        return redirect(url_for("user_profile", username=session[USERNAME]))

    else:
        return render_template("user_register_form.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Show/process login form.
    Ensures user authentication and then directs to user's profile
    """

    if USERNAME in session:
        return redirect(url_for("user_profile", username=session[USERNAME]))

    form = LoginForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        user = User.authenticate(**data)

        if user:
            session[USERNAME] = user.username
            return redirect(url_for("user_profile", username=session[USERNAME]))
        else:
            form.username.errors = ["Bad name/password"]

    return render_template("user_login_form.html", form=form)


@app.get("/users/<username>")
def user_profile(username):
    """Show user profile"""

    if USERNAME not in session or session[USERNAME] != username:
        raise Unauthorized()

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

    return redirect(url_for("homepage"))


@app.post("/users/<username>/delete")
def delete_user(username):
    """Deletes user and all their posts"""

    if USERNAME not in session or session[USERNAME] != username:
        raise Unauthorized()

    form = CSRFProtectForm()

    if form.validate_on_submit():
        user = User.query.get_or_404(username)
        # notes = Note.query.filter(Note.owner_username == username).all()
        Note.query.filter(Note.owner_username == username).delete()
        # for note in notes:
        #     db.session.delete(note)

        session.pop(USERNAME, None)

        db.session.delete(user)
        db.session.commit()
        flash(f"User {username} deleted.")

    else:
        raise Unauthorized()

    return redirect(url_for("homepage"))


@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def add_note(username):
    """shows add note form and processes input to add to db on submit"""

    if USERNAME not in session or session[USERNAME] != username:
        raise Unauthorized()

    form = NoteForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        new_note = Note.add_note(**data, owner_username=username)

        db.session.add(new_note)
        db.session.commit()

        return redirect(url_for("user_profile", username=session[USERNAME]))

    else:
        return render_template("add_note.html", form=form)


@app.route("/notes/<note_id>/update", methods=["GET", "POST"])
def edit_note(note_id):
    """shows edit note form and processes input to edit existing note on submit"""

    note = Note.query.get_or_404(note_id)

    if USERNAME not in session or session[USERNAME] != note.owner_username:
        raise Unauthorized()

    form = NoteForm(obj=note)

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        note.edit_note(**data)

        db.session.commit()

        return redirect(url_for("user_profile", username=session[USERNAME]))

    else:
        return render_template("edit_note.html", form=form, note=note)


@app.post("/notes/<note_id>/delete")
def delete_note(note_id):
    """Deletes post, returns to user profile"""

    note = Note.query.get_or_404(note_id)

    if USERNAME not in session or session[USERNAME] != note.owner_username:
        raise Unauthorized()

    form = CSRFProtectForm()

    if form.validate_on_submit():
        db.session.delete(note)
        db.session.commit()
        flash(f"Note {note.title} deleted.")
    else:
        raise Unauthorized()

    return redirect(url_for("user_profile", username=session[USERNAME]))
