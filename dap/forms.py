from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Required
from .db import UIUsers


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()],render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    access = RadioField('Access', choices = [('admin','Admin'),('user','User')], validators=[DataRequired()])    
    submit = SubmitField('Sign Up!')

    def validate_username(self, username):
        user = UIUsers.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Username already taken! Try a different one ')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()],render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
