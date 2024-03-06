from wtforms import (
    StringField,
    BooleanField,
    validators,
    SubmitField,
    SelectField,
)
from flask_wtf import FlaskForm



class ForCliente(FlaskForm):
    pjoucpf = BooleanField()
    nome = StringField("Nome Completo:",[validators.DataRequired(),])
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
        "Email :",
        [
            validators.Optional(),
            validators.Email(message="E-mail não é Valido. Ex:exemplo@exemplo.com"),
        ],
    )
    niver = StringField(
        "Data de nacimento :",
        [
            validators.Optional(),
            validators.Length(min=10, message="Data invalido. Ex:XX/XX/XXXX"),
        ],
    )
    cpf = StringFieldfone = StringField(
        "CPF : ",
        [
            validators.Optional(),
            validators.Length(min=14, message="CPF invalido. Ex:XXX.XXX.XXX-XX"),
        ],
    )
    rg = StringFieldfone = StringField(
        "RG : ",
    )
    razaoSocial = StringField(
        "Razão Social :",
        [validators.Optional()],
    )
    nomeFantasia = StringField(
        "Nome Social :",
        [
            validators.Optional(),
        ],
    )
    cnpj = StringField(
        "CNPJ :",
        [
            validators.Optional(),
            validators.Length(min=18, message="CNPJ invalido. Ex:XX.XXX.XXX/XXXX-XX"),
        ],
    )
    cep = StringField(
        "CEP :",
        [
            validators.Optional(),
            validators.Length(min=9, message="CEP invalido. Ex:XXXXX-XXX"),
        ],
    )
    estado = StringField("Estado :")
    cidade = StringField("Cidade :")
    bairro = StringField("Bairro :")
    rua = StringField("Nome da Rua :")
    nuCasa = StringField("Numero: ")
    complemento = StringField("Complemento :")
    statu = SelectField(
        "Status :", choices=[("ATIVO", "ATIVO"), ("BLOQUEADO", "BLOQUEADO")]
    )
    submit = SubmitField("Adicionar")


class ForVeiculo(FlaskForm):
    placa = StringField(
        "Placa: ",
        [
            validators.DataRequired(),
            validators.Length(
                min=8, message="Formato da PLACA Errado. ex:AAA-9999 ou AAA-9A99"
            ),
        ],
    )
    km = StringField("Km:")
    chassi = StringField("Chassi:")
    submit = SubmitField("ADICIONAR")
