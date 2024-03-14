from wtforms import (
    StringField,
    TextAreaField,
    validators,
    SubmitField,
)
from flask_wtf import FlaskForm


class Addpecas(FlaskForm):
    nome = StringField("Nome:", [validators.DataRequired()])
    codigo = StringField("Codigo da Peça:", [validators.DataRequired()])
    codigo_debarra = StringField("Codigo de Barra:")
    pago = StringField("Valor/Pago:", [validators.DataRequired()])
    preso = StringField("Preço:", [validators.DataRequired()])
    estoque = StringField("Estoque:", [validators.DataRequired()])
    descrisao = TextAreaField("Descrição:")

    submit = SubmitField("ADICIONAR")
