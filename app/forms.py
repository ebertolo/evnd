from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField 
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    """ Formulario para Login, Derivado da classe Form"""
        
    email = EmailField('email', validators=[DataRequired(), Length(min=1, max=100, message="Email deve ter até 100 caracteres."), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    password2 = PasswordField('password2', validators=[DataRequired(), EqualTo('password', message='Senhas devem ser iguais.')])
    remember_me = BooleanField('Manter-me logado')
    submit = SubmitField('Entrar', [DataRequired()])