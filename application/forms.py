from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField, StringField, PasswordField, BooleanField, FileField
from wtforms.validators import Length, InputRequired, ValidationError, NumberRange, EqualTo, Regexp
from application.models import User
from werkzeug.utils import secure_filename
import os


class RegistrationForm(FlaskForm):
    # Create Field for User to Enter Username, Email, Password, and Confirm Password
    # Check if Username contains spaces
    # Check if Username is between 4 and 20 characters
    # Check if Password is between 8 and 20 characters
    # Check if Password and Confirm Password are the same
    username = StringField('Username', validators = [InputRequired (message = 'Please enter a username'), Regexp(r'^[\w.@+-]+$', message = 'Invalid username!'),  Length(min=4, max=20, message = 'Username must be between 4 and 20 characters')])
    password = PasswordField('Password', validators = [InputRequired (message = 'Please enter a password'), Regexp(r'^[\w.@+-]+$', message = 'Invalid password!'), Length(min=8, max=20, message = 'Password must be between 8 and 20 characters')])
    confirm_password = PasswordField('Confirm Password', validators = [InputRequired (message = 'Please confirm your password'), EqualTo('password', message = 'Passwords must match')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Check if Username is already in the database
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError('Username already exists. Please select a different username.')

    # check if username and password are the same
    def validate_password(self, password):
        if password.data == self.username.data:
            raise ValidationError('Password cannot be the same as username.')
    
class LoginForm(FlaskForm):
    # Create Field for User to Enter Username and Password
    username = StringField('Username', validators=[InputRequired(message = 'Please enter username!'), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(message = 'Please enter password!'), Length(min=4, max=80)])
    rememberme = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PredictionForm(FlaskForm):
    file = FileField('File', validators = [InputRequired(message = 'Upload Image File!')])
    Model_selection = SelectField(u'Choose a Model: ', validators = [InputRequired (message = 'Please choose a model!')], choices=[(0, 'NathanNet-v1'), (1, 'NathanNet-v2')])
    predict = SubmitField('Upload and Predict')

    




