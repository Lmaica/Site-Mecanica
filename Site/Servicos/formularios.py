from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired



class Responsaveis(FlaskForm):
    vendedor = SelectField(
        "Vendedor:",
        validators=[DataRequired()],
    )
    mecanico = SelectField(
        "Mecanico:",
        validators=[DataRequired()],
    )
