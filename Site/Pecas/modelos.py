from Site import db, app
from datetime import datetime, timezone


class Marcapeca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)


class Peca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String, nullable=False)
    codigo_debarra = db.Column(db.String, nullable=False)
    nome = db.Column(db.String, nullable=False)
    pago = db.Column(db.String, nullable=False)
    preso = db.Column(db.String, nullable=False)
    estoque = db.Column(db.Integer, nullable=False)
    carro = db.Column(db.JSON, unique=False, default="TODOS")
    descrisao = db.Column(db.Text, nullable=False)

    marca_id = db.Column(db.Integer, db.ForeignKey("marcapeca.id"), nullable=False)
    marca = db.relationship("Marcapeca", backref=db.backref("marca", lazy=True))

    fornecedor_id = db.Column(
        db.Integer, db.ForeignKey("fornecedor.id"), nullable=False
    )
    fornecedor = db.relationship(
        "Fornecedor", backref=db.backref("fornecedor", lazy=True)
    )

    image_1 = db.Column(
        db.String(180), unique=False, nullable=False, default="foto.jpg"
    )
    image_2 = db.Column(
        db.String(180), unique=False, nullable=False, default="foto.jpg"
    )
    image_3 = db.Column(
        db.String(180), unique=False, nullable=False, default="foto.jpg"
    )
    data_criado = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )

    def __repr__(self):
        return "<Peca %r>" % self.nome


with app.app_context():
    db.create_all()
    if Marcapeca.query.count() == 0:
        BOSCH = Marcapeca(nome="BOSCH")
        db.session.add(BOSCH)
        db.session.commit()
