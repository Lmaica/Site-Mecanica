from Site import db, app, BaseDados


class Cliente(BaseDados):
    senha = db.Column(db.String, unique=False)
    statu = db.Column(db.String, unique=False)
    pjoucpf = db.Column(db.Boolean)


class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String, unique=False)
    carro_id = db.Column(db.Integer, db.ForeignKey("carro.id"), nullable=False)
    carro = db.relationship("Carro", backref=db.backref("carro", lazy=True))
    km = db.Column(db.Integer, nullable=False)
    chassi = db.Column(db.Integer, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    cliente = db.relationship("Cliente", backref=db.backref("cliente", lazy=True))

    def __repr__(self):
        return "<Veiculo %r>" % self.placa


with app.app_context():
    db.create_all()
