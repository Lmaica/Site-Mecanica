from wtforms import (
    StringField,
    TextAreaField,
    validators,
    SubmitField,
    SelectField,
)
from flask_wtf import FlaskForm
from .modelos import Catfornecedor
from wtforms.validators import DataRequired


class ForFornecedor(FlaskForm):
    nome = StringField("Nome:", [validators.DataRequired()])
    obs = TextAreaField("Obiservação :")
    fone = StringField(
        "Telefone :",
        [
            validators.DataRequired(),
            validators.Length(min=11, message="O Telefone tem que ter 11 Digitos"),
        ],
    )
    fone1 = StringField(
        "Telefone 2 :",
        [
            validators.Optional(),
            validators.Length(min=15, message="O Telefone tem que ter 11 Digitos"),
        ],
    )
    email = StringField("Email :")
    cnpj = StringField("CNPJ: ")
    cep = StringField("CEP : ")
    estado = StringField("Estado :")
    cidade = StringField("Cidade :")
    bairro = StringField("Bairro :")
    rua = StringField("Nome da Rua :")
    nuCasa = StringField("Numero : ")
    complemento = StringField("Complemento :")
    catfornecedor = SelectField(
        "Categoria :",
        choices=[
            ("", "Selecione Categoria"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("ADICIONAR")

    def __init__(self, *args, **kwargs):
        super(ForFornecedor, self).__init__(*args, **kwargs)
        self.catfornecedor.choices += [
            (catfornecedor.id, catfornecedor.nome) for catfornecedor in Catfornecedor.query.all()
        ]
