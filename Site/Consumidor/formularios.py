from wtforms import (
    StringField,
    BooleanField,
    validators,
    SubmitField,
    SelectField,
    PasswordField,
)
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo
from wtforms.validators import Length

class EmailConsumidor(FlaskForm):
    email = StringField('E-mail', validators=[validators.DataRequired(), validators.Email()])
    confirm_email = StringField('Confirmar E-mail', validators=[validators.DataRequired(), validators.EqualTo('email', message='Emails devem ser iguais')])

class CriarConsumidor(FlaskForm):
    nome = StringField("Nome Completo:")
    fone = StringField("Telefone :")
    senha = PasswordField('Senha:')
    confirmacao_senha = PasswordField('Confirme a Senha:')

