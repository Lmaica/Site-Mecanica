from Site import db, app
from Site.Global.fun_global import Calculos_gloabal
from datetime import datetime, timezone


class Carteirabanco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)


class Catcaixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)


class Caixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pagopor = db.Column(db.String, nullable=False)
    descricao = db.Column(db.String, nullable=False)
    valor = db.Column(db.String, nullable=False)
    data_criado = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )
    tipo = db.Column(db.String, nullable=False)
    carteira_id = db.Column(
        db.Integer, db.ForeignKey("carteirabanco.id"), nullable=False
    )
    carteira = db.relationship(
        "Carteirabanco", backref=db.backref("carteira", lazy=True)
    )
    catcaixa_id = db.Column(db.Integer, db.ForeignKey("catcaixa.id"), nullable=False)
    catcaixa = db.relationship("Catcaixa", backref=db.backref("catcaixa", lazy=True))
    fornecedor_id = db.Column(
        db.Integer, db.ForeignKey("fornecedor.id"), nullable=False
    )
    fornecedor = db.relationship(
        "Fornecedor", backref=db.backref("Fornecedor", lazy=True)
    )

    def Saldo_Caixa():
        registros_caixa = Caixa.query.all()
        saldo_caixa = 0
        for registro in registros_caixa:
            valor_calculado = Calculos_gloabal.valor_para_Calculos(registro.valor)
            if registro.tipo == "Saida":
                saldo_caixa -= valor_calculado
            else:
                saldo_caixa += valor_calculado
        total_caixa = Calculos_gloabal.format_valor_moeda(saldo_caixa)
        return total_caixa


with app.app_context():
    db.create_all()
    if Catcaixa.query.count() == 0:
        SERVIÇO = Catcaixa(nome="*SERVIÇO*")
        TRASFERIR = Catcaixa(nome="*TRASFERIR*")
        PEÇAS = Catcaixa(nome="PEÇAS")
        GANHOS = Catcaixa(nome="*GANHOS*")
        db.session.add(SERVIÇO)
        db.session.add(TRASFERIR)
        db.session.add(PEÇAS)
        db.session.add(GANHOS)
        db.session.commit()
    if Carteirabanco.query.count() == 0:
        DINHERO = Carteirabanco(nome="DINHERO")
        db.session.add(DINHERO)
        db.session.commit()
