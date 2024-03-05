from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class AddCaixas(FlaskForm):
    pagopor = StringField("Pago Por", validators=[DataRequired()])
    descricao = StringField("Descrição", validators=[DataRequired()])
    valor = StringField("Valor", validators=[DataRequired()])
    carteira_id = SelectField("Carteira", validators=[DataRequired()])
    catcaixa_id = SelectField("Categoria", validators=[DataRequired()])
    fornecedor_id = SelectField("Fornecedor", validators=[DataRequired()])
    submit = SubmitField("ADICIONAR")
