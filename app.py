import os

from flask import Flask, redirect, session

from models import connect_db, db, User

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "postgresql:///notes")

connect_db(app)
db.create_all()

@app.get('/')
def redirect_to_register():
    """Redirect to register page"""

    return redirect('/register')

@app.route('/register', methods=["GET","POST"])
def register_user():
    """Register a user to db, re render form on invalid input
        If valid input, redirect to user profile page
    """
