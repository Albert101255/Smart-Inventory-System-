from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional

class UserForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    role = SelectField('Role', choices=[('admin','Admin'),('manager','Manager'),('staff','Staff')], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save User')
