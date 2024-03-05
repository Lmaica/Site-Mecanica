from Site import db, app, BaseDados


class Catfornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)


class Fornecedor(BaseDados):
    catfornecedor_id = db.Column(
        db.Integer, db.ForeignKey("catfornecedor.id"), nullable=False
    )
    catfornecedor = db.relationship(
        "Catfornecedor", backref=db.backref("catfornecedor", lazy=True)
    )
    obs = db.Column(db.Text, nullable=False, default="")


with app.app_context():
    db.create_all()
    if Catfornecedor.query.count() == 0:
        PEÇAS = Catfornecedor(nome="PEÇAS")
        db.session.add(PEÇAS)
        db.session.commit()
