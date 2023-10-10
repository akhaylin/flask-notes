from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class RegisterForm(FlaskForm):
    """User registration form"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)]
    )
#TODO: put min password length
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(max=72)]
    )

    email = StringField(
        "Email Address",
        validators=[InputRequired(), Length(max=50), Email()]
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)]
    )

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )

class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""