from Site import db, app


class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_fip = db.Column(db.String, nullable=True)
    marca = db.Column(db.String, nullable=True)
    ano = db.Column(db.String, nullable=True)
    modelo = db.Column(db.String, nullable=True)
    motor = db.Column(db.String, nullable=True)


with app.app_context():
    db.create_all()

