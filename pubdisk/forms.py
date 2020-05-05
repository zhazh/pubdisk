# -*- coding: utf-8 -*-
"""
:author: Zhazh
:copyright: © 2020 Zhazh <zhazh1985@163.com>
:license: MIT, see LICENSE for more details.
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField, SelectMultipleField, RadioField, 
                IntegerField, FloatField, FileField, TextAreaField,  DateTimeField, HiddenField, SubmitField)
from wtforms.validators import (ValidationError, 
                DataRequired, InputRequired, NumberRange, Email, EqualTo, Length,
                Regexp, URL, AnyOf, NoneOf)
from sqlalchemy import func, exists, and_, or_
from flask import current_app
import os

class LoginForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message='Username required'), 
        Length(1,20, message='Length between 1 and 20')
    ])
    password = PasswordField('password', validators=[
        DataRequired(message='Password required'), 
        Length(5,20, message='Length between 5 and 20')
    ])
    remember_me = BooleanField('Remember me', default=False)
    submit = SubmitField('Sign in')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('old_password', validators=[
        DataRequired(message='Old password required.')
    ])
    new_password = PasswordField('new_password', validators=[
        Length(5, 20, message='Length must between 5 and 20')
    ])
    confirm_new_password = PasswordField('confirm_new_password', validators=[
        EqualTo('new_password', message='Must be the same value.')
    ])

class NewUserForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message="User's name required.")
    ])

    userhome = StringField('userhome')

    def validate_userhome(form, field):
        home = field.data.strip()
        if home == '':
            raise ValidationError("User's home required.")
        else:
            root = current_app.config.get('USERS_ROOT')
            localhome = os.path.join(root, home[1:].replace('/', os.path.sep))
            if not os.path.isdir(localhome):
                raise ValidationError("User's home invalid.")


