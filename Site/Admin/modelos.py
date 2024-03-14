from Site import db, BaseDados, app, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone


class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)


class Metasbruto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meta = db.Column(db.String, nullable=False)
    bonos = db.Column(db.String, nullable=False)
    dataModific = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )


class Metasliquido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meta = db.Column(db.String, nullable=False)
    bonos = db.Column(db.String, nullable=False)
    dataModific = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )

class Metasmecanico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meta = db.Column(db.String, nullable=False)
    bonos = db.Column(db.String, nullable=False)
    dataModific = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )

class Metasvendedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meta = db.Column(db.String, nullable=False)
    bonos = db.Column(db.String, nullable=False)
    dataModific = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )

class Lembretestodos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    msg = db.Column(db.String, nullable=False)
    autor = db.Column(db.String, nullable=False)
    destinatario = db.Column(db.String, nullable=False)
    tipo = db.Column(db.String, nullable=False)
    data_inicil = db.Column(db.String, nullable=False)
    data_fim = db.Column(db.String, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(BaseDados, UserMixin):
    apelido = db.Column(db.String, unique=False)
    senha = db.Column(db.String, unique=False)
    nivel = db.Column(db.String, unique=False)
    status = db.Column(db.String, unique=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey("cargo.id"), nullable=False)
    cargo = db.relationship("Cargo", backref=db.backref("cargo", lazy=True))

    def __repr__(self):
        return "<User %r>" % self.nome


with app.app_context():
    db.create_all()
    if Metasbruto.query.count() == 0:
        valor_hora_inicial = Metasbruto(meta="R$ 20.000,00", bonos="R$ 40.000,00")
        db.session.add(valor_hora_inicial)
        db.session.commit()
    if Metasliquido.query.count() == 0:
        valor_hora_inicial = Metasliquido(meta="R$ 10.000,00", bonos="R$ 20.000,00")
        db.session.add(valor_hora_inicial)
        db.session.commit()
    if Metasmecanico.query.count() == 0:
        valor_hora_inicial = Metasmecanico(meta="R$ 2.000,00", bonos="R$ 4.000,00")
        db.session.add(valor_hora_inicial)
        db.session.commit()
    if Metasvendedor.query.count() == 0:
        valor_hora_inicial = Metasvendedor(meta="R$ 2.000,00", bonos="R$ 4.000,00")
        db.session.add(valor_hora_inicial)
        db.session.commit()
    if Cargo.query.count() == 0:
        cargos = [
            Cargo(nome="*PRESIDENTE*"),
            Cargo(nome="*VENDEDOR*"),
            Cargo(nome="*MECANICO*"),
        ]
        for cargo in cargos:
            db.session.add(cargo)

        db.session.commit()
    if User.query.count() == 0:
        hash_senha = bcrypt.generate_password_hash("MUDAR.EMAIL@MUDAR.com")
        cadastrar = User(
            nome="",
            apelido="",
            fone="",
            email="MUDAR.EMAIL@MUDAR.com",
            senha=hash_senha,
            foto="foto.jpg",
            nivel="DONO",
            status="ATIVO",
            cargo_id=1,
        )
        db.session.add(cadastrar)
        db.session.commit()
