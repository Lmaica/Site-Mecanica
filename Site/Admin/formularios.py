from wtforms import (
    Form,
    StringField,
    PasswordField,
    validators,
    SubmitField,
    SelectField,
    TextAreaField,
    DateField,
)
from flask_wtf import FlaskForm
from .modelos import User, Cargo
from wtforms.validators import DataRequired, EqualTo
from sqlalchemy import not_
from wtforms.validators import Length

class LembretesMensagens(FlaskForm):
    titulo = StringField("Titulo:", [validators.DataRequired()])
    msg = TextAreaField("Mensagem:", [validators.DataRequired()])
    data_inicial = DateField("Data Inicial:", [validators.DataRequired()])
    data_fim = DateField("Data Final:", [validators.DataRequired()])

    destinatario = SelectField(
        "Destinatario:",
        choices=[
            ("", "Selecione Destinatario"),
            ("TODOS", "Todos"),
        ],
        validators=[DataRequired()],
    )

    tipo = SelectField(
        "Tipo:",
        choices=[
            ("", "Selecione Tipo"),
            ("AVISO", "Aviso"),
            ("ADIVERTENCIA", "Adivertencia"),
        ],
        validators=[DataRequired()],
    )

    def __init__(self, *args, **kwargs):
        super(LembretesMensagens, self).__init__(*args, **kwargs)

        self.destinatario.choices += [
            (destinatario.nome, destinatario.nome) for destinatario in Cargo.query.all()
        ]
        self.destinatario.choices += [
            (destinatario.apelido, destinatario.apelido)
            for destinatario in User.query.all()
        ]


class RegistrationForm(FlaskForm):
    nome = StringField("Nome Completo:", [validators.DataRequired()])
    apelido = StringField(
        "Apelido:",
        [
            validators.DataRequired(),
            validators.Length(
                max=15, message="O apelido pode ter no máximo 15 caracteres."
            ),
        ],
    )
    fone = StringField(
        "Telefone :",
        [
            validators.DataRequired(),
            validators.Length(min=15, message="O Telefone tem que ter 11 Digitos"),
        ],
    )
    fone1 = StringField(
        "Telefone 2 :",
        [
            validators.Optional(),
            validators.Length(min=15, message="O Telefone tem que ter 11 Digitos"),
        ],
    )
    email = StringField(
        "E-mail :",
        [validators.Email(message="E-mail Invalido"), validators.DataRequired()],
    )
    niver = StringField(
        "Data de nacimento:",
        [
            validators.Optional(),
            validators.Length(min=10, message="Data invalido. Ex: XX/XX/XXXX"),
        ],
    )
    cpf = StringFieldfone = StringField(
        "CPF: ",
        [
            validators.Optional(),
            validators.Length(min=14, message="CPF invalido. Ex: XXX.XXX.XXX-XX"),
        ],
    )
    rg = StringFieldfone = StringField(
        "RG: ",
        [
            validators.Optional(),
            validators.Length(min=8, message="RG invalido. Ex: XXXXXXXX"),
        ],
    )
    razaoSocial = StringField("Razão Social:")
    nomeFantasia = StringField("Nome Social:")
    cnpj = StringField(
        "CNPJ:",
        [
            validators.Optional(),
            validators.Length(min=18, message="CNPJ invalido. Ex: XX.XXX.XXX/XXXX-XX"),
        ],
    )
    cep = StringField(
        "CEP:",
        [
            validators.Optional(),
            validators.Length(min=9, message="CEP invalido. Ex: XXXXX-XXX"),
        ],
    )
    estado = StringField("Estado :")
    cidade = StringField("Cidade :")
    bairro = StringField("Bairro :")
    rua = StringField("Nome da Rua :")
    nuCasa = StringField("Numero: ")
    complemento = StringField("Complemento :")
    nivel = SelectField(
        "Nivel :",
        choices=[
            ("", "Selecione Nivel"),
            ("PERITO", "PERITO(master)"),
            ("ESPECIALISTA", "ESPECIALISTA(alto)"),
            ("COMPETENTE", "COMPETENTE(medio)"),
            ("INEXPERIENTE", "INEXPERIENTE(medio-baixo)"),
            ("NOVATO", "NOVATO(baixo)"),
        ],
        validators=[DataRequired()],
    )
    status = SelectField(
        "Status:", choices=[("ATIVO", "ATIVO"), ("BLOQUEADO", "BLOQUEADO")]
    )
    cargo = SelectField(
        "Cargo:",
        choices=[
            ("", "Selecione Cargo"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("ADICIONAR")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.cargo.choices += [
            (cargo.id, cargo.nome)
            for cargo in Cargo.query.filter(not_(Cargo.id == 1)).all()
        ]

class AlterarSenhaForm(FlaskForm):
    senha_nova = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=8)])
    confirmacao_senha = PasswordField('Confirme a Nova Senha', validators=[DataRequired(), EqualTo('senha_nova')])
    submit = SubmitField('ALTERAR SENHA')

class LoginFormulario(Form):
    email = StringField(
        "",
        [validators.DataRequired(message="E-mail ou senha Invalido")],
    )
    senha = PasswordField("", [validators.DataRequired()])
