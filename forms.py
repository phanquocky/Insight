from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, HiddenField, BooleanField, IntegerField, FormField
from mongodb import query_users_by_username
from mongodb import User
from Keypair.hash import sha256_hash

class SignupForm(Form):
    username = StringField('Username',  [
        validators.DataRequired('Please enter your username.'),
        validators.Length(max=30, message='Username is at most 30 characters.'),
    ])
    
    password = PasswordField('Password', [
        validators.DataRequired('Please enter a password.'),
        validators.Length(min = 6, message='Passwords is at least 6 characters.'),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    public_key = StringField('Public key', [
        validators.DataRequired('Please generate your keys.'),
    ])
    private_key = StringField('Private key', [
        validators.DataRequired('Please generate your keys.'),
    ])
    submit = SubmitField('Create account')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self, extra_validators=None):
        if not Form.validate(self):
            return False

        user = query_users_by_username(username = self.username.data)
        if user is not None:
            self.username.errors.append('That username is already taken.')
            return False

        return True
    
class LoginForm(Form):
    username = StringField('Username',  [
        validators.DataRequired('Please enter your username.'),
        validators.Length(max=30, message='Username is at most 30 characters.'),
    ])
    password = PasswordField('Password', [
        validators.DataRequired('Please enter a password.'),
        validators.Length(min=6, message='Passwords is at least 6 characters.'),
    ])
    submit = SubmitField('Sign In')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self, extra_validators=None):
        if not Form.validate(self):
            return False

        user = query_users_by_username(username = self.username.data)
        if user and check_password(user['password'], self.password.data.encode('utf-8')):
            return True
        else:
            self.password.errors.append('Invalid username or password')
            return False

def check_password(password, text):
    if password == sha256_hash(text):
            return True
    return False
        

