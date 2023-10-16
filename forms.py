from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, HiddenField, BooleanField, IntegerField, FormField
from mongodb_ver2 import query_user_by_username
from mongodb_ver2 import User

class SignupForm(Form):
    username = StringField('Username',  [
        validators.DataRequired('Please enter your username.'),
        validators.Length(max=50, message='Username is at most 50 characters.'),
    ])
    score = IntegerField('Score')
    metamask_id = StringField('Metamask ID', [
        validators.DataRequired('Please connect to Metamask.'),
    ])
    submit = SubmitField('Create account')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self, extra_validators=None):
        print('hihi')
        if not Form.validate(self):
            print('haha')
            return False

        user = query_user_by_username(username = self.username.data)
        print(user)
        if user is not None:
            self.username.errors.append('That username is already taken.')
            return False

        return True
    
class LoginForm(Form):
    username = StringField('Username',  [
        validators.DataRequired('Please enter your username.'),
        validators.Length(max=50, message='Username is at most 50 characters.'),
    ])
    score = IntegerField('Score')
    metamask_id = StringField('Metamask ID', [
        validators.DataRequired('Please connect to Metamask.'),
    ])
    submit = SubmitField('Sign In')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self, extra_validators=None):
        if not Form.validate(self):
            return False

        user = query_user_by_username(username = self.username.data)
        if user and query_user_by_username(self.username.data)['metamask_id'] == self.metamask_id.data:
            return True
        else:
            self.username.errors.append('Invalid username or metamask id.')
            return False

        

