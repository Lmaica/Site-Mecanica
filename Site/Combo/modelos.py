from Site import db, app
from datetime import datetime, timezone


class Combo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    atividade = db.Column(db.String, nullable=True, default=None)
    status = db.Column(db.String, nullable=False, default="Normal")
    data_inicil_combo= db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )
    data_final_combo = db.Column(
        db.DateTime, default=None, nullable=True
    )
    carro = db.Column(db.JSON, unique=False, default="")
    peca_os_combo = db.Column(db.String, nullable=False)
    mo_os_combo = db.Column(db.String, nullable=False)

    obs = db.Column(db.String, nullable=False, default="")
    image_1 = db.Column(
        db.String(180), unique=False, nullable=False, default="foto.jpg"
    )



with app.app_context():
    db.create_all()