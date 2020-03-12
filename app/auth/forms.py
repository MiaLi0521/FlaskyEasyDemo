from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    """登录表单"""
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Kepp me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """注册表单"""
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'User names must have only letters,numbers,dots or underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        """后端数据库验证邮箱是否已注册"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """后端验证同名用户是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='password must match')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    submit = SubmitField('Reset password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('password2', message='Passwords')])
    password2 = PasswordField('Confirmed Password', validators=[DataRequired()])
    submit = SubmitField('Reset password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
