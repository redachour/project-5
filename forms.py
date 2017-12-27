from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from models import Entry


def date(form, field):
    '''Check if the date field is on the right format'''
    try:
        datetime.strptime(field.data, '%m/%d/%Y')
    except ValueError:
        raise ValidationError('Date format is not valid')


def num(form, field):
    '''Check if time spent field is valid'''
    try:
        float(field.data)
    except ValueError:
        raise ValidationError('This field should be a float or integer')


def title(form, field):
    '''Check if title is unique'''
    if Entry.select().where(Entry.title == field.data).exists():
        raise ValidationError('Entry title already exists.')


class AddEditForm(FlaskForm):
    title = StringField('Entry Title', validators=[DataRequired(), title])
    date = StringField('Date (MM/DD/YYYY)', validators=[DataRequired(), date])
    time_spent = StringField('Time Spent (MIN)',
                             validators=[DataRequired(), num])
    learned = TextAreaField('What I Learned', validators=[DataRequired()])
    resources = TextAreaField('Resources', validators=[DataRequired()])
    tags = StringField('Tags seperated with a space',
                       validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
