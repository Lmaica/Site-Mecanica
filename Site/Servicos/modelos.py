from Site import db, app
from datetime import datetime, timezone


class Serviso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notafiscal = db.Column(db.String, unique=False, nullable=False, default="")
    status = db.Column(db.String, nullable=False, default="Orçamento")
    cliente_veiculo = db.Column(db.String, nullable=False)
    data_criado = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )
    data_finalizada = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )
    peca_os = db.Column(db.String, nullable=False)
    mo_os = db.Column(db.String, nullable=False)

    obs = db.Column(db.String, nullable=False, default="")
    km_final = db.Column(db.String, nullable=False, default="")
    carteira_id = db.Column(db.String, nullable=False, default="")
    valor_pesas = db.Column(db.String, nullable=False, default="")
    valor_mdo = db.Column(db.String, nullable=False, default="")
    valor_gasto = db.Column(db.String, nullable=False, default="")
    valor_recebido = db.Column(db.String, nullable=False, default="")
    valor_total = db.Column(db.String, nullable=False, default="")
    desconto_sobra = db.Column(db.String, nullable=False, default="")
    valor_ganho = db.Column(db.String, nullable=False, default="")

    cliente_os_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    cliente_os = db.relationship("Cliente", backref=db.backref("cliente_os", lazy=True))

    veiculo_os_id = db.Column(db.Integer, db.ForeignKey("veiculo.id"), nullable=False)
    veiculo_os = db.relationship("Veiculo", backref=db.backref("veiculo_os", lazy=True))

    user_os_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user_os = db.relationship(
        "User", foreign_keys=[user_os_id], backref=db.backref("user_os", lazy=True)
    )

    mecanico_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    mecanico = db.relationship(
        "User", foreign_keys=[mecanico_id], backref=db.backref("mecanico", lazy=True)
    )

    vendedor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    vendedor = db.relationship(
        "User", foreign_keys=[vendedor_id], backref=db.backref("vendedor", lazy=True)
    )
    editor_finalizado_id = db.Column(db.String, nullable=False, default="")
    data_atulizado_finalizado = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )

class Registrospreservados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serviso_id = db.Column(db.Integer, db.ForeignKey('serviso.id'))
    serviso = db.relationship('Serviso', backref=db.backref('serviso', lazy=True))
    modo_aprovado = db.Column(db.String)
    descricao = db.Column(db.String)
    obs = db.Column(db.String)
    status = db.Column(db.String, default=False)
    images_carro = db.Column(db.Text, default="[]")
    videos_carro = db.Column(db.Text, default="[]")
    images_serviso = db.Column(db.Text, default="[]")
    videos_serviso = db.Column(db.Text, default="[]")
    image_token = db.Column(db.String, unique=False, nullable=False, default="foto.jpg")
    token = db.Column(db.String, unique=False, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False)
    
    
with app.app_context():
    db.create_all()
