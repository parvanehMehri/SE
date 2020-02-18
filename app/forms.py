from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField(
        'Password2', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class SendMassage_addFriend(FlaskForm):
    massage=TextAreaField('massage',validators=[DataRequired()])
    receiver=StringField('receiver',validators=[DataRequired()])
    addfriend=StringField('addfriend',validators=[DataRequired()])
    add = SubmitField('add')
    submit = SubmitField('Send')

class CourseForm(FlaskForm) :
    enroll = SubmitField('Enroll Me')
    remind = SubmitField('Remind Me Later')

class ProfileForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    field_selection = StringField('field_selection', validators=[DataRequired()])
    university_selection = StringField('university_selection', validators=[DataRequired()])
    bio = StringField('bio', validators=[DataRequired()])
    submitProfile = SubmitField('submitProfile')

    password = PasswordField('password')
    # password2 = PasswordField(
    #     'Password2', validators=[DataRequired(), EqualTo('password')])
    changePassword = SubmitField('changePassword')


