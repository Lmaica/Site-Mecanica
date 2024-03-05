from Site import db, app
from datetime import datetime, timezone


class Valorhora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.String, nullable=False, default="R$ 100,00")
    dataModific = db.Column(db.DateTime, unique=False, default=datetime.utcnow)


class Catmaoobra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)


class Nomemaoobra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)


class Maoobra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomemaoobra_id = db.Column(
        db.Integer, db.ForeignKey("nomemaoobra.id"), nullable=False
    )
    nomemaoobra = db.relationship(
        "Nomemaoobra", backref=db.backref("nomemaoobra", lazy=True)
    )
    tempo = db.Column(db.String, nullable=False)
    preso = db.Column(db.String, nullable=False, default="R$ 0,00")
    marca = db.Column(db.String, unique=False, default="TODOS")
    modelo = db.Column(db.String, unique=False, default="TODOS")
    anoIni = db.Column(db.String, unique=False, default="TODOS")
    anoFin = db.Column(db.String, unique=False, default="TODOS")
    motor = db.Column(db.String, unique=False, default="TODOS")
    catmaoobra_id = db.Column(
        db.Integer, db.ForeignKey("catmaoobra.id"), nullable=False
    )
    catmaoobra = db.relationship(
        "Catmaoobra", backref=db.backref("catmaoobra", lazy=True)
    )
    obs = db.Column(db.Text, nullable=False, default="")
    data_criado = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )

    def __repr__(self):
        return "<AddMaoObra %r>" % self.marca


with app.app_context():
    db.create_all()
    if Valorhora.query.count() == 0:
        valor_hora_inicial = Valorhora(valor="R$ 100,00")
        db.session.add(valor_hora_inicial)
        db.session.commit()
    if Nomemaoobra.query.count() == 0:
        TROCA = Nomemaoobra(nome="TROCA DE CORREIA DENTADA")
        db.session.add(TROCA)
        db.session.commit()
    if Catmaoobra.query.count() == 0:
        MOTOR = Catmaoobra(nome="MOTOR")
        db.session.add(MOTOR)
        SUSPENÇÃO = Catmaoobra(nome="SUSPENÇÃO")
        db.session.add(SUSPENÇÃO)
        db.session.commit()
