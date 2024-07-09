from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
from flask_login import LoginManager, current_user
from functools import wraps
from flask_migrate import Migrate
import json
from authlib.integrations.flask_client import OAuth

def ajustes():
    from Site.Admin import modelos
    from Site.Carros import modelos
    from Site.Clientes import modelos
    from Site.MaoObra import modelos
    from Site.Fornecedor import modelos
    from Site.Pecas import modelos
    from Site.Caixa import modelos
    from Site.Servicos import modelos
    from Site.Combo import modelos
    from Site.Consumidor import modelos

    # rotas
    from Site.Admin import rotas
    from Site.Carros import rotas
    from Site.Clientes import rotas
    from Site.MaoObra import rotas
    from Site.Pecas import rotas
    from Site.Fornecedor import rotas
    from Site.Servicos import rotas
    from Site.Caixa import rotas
    from Site.Combo import rotas
    from Site.Consumidor import rotas


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder='static')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "BancoOficina.db"
)
app.config["SECRET_KEY"] = "LMM1992"
db = SQLAlchemy(app)



class BaseDados(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=False, nullable=False)
    fone = db.Column(db.Integer, unique=False)
    fone1 = db.Column(db.Integer, unique=False)
    email = db.Column(db.String, unique=False)
    niver = db.Column(db.Integer, unique=False)
    razaoSocial = db.Column(db.String, unique=False)
    nomeFantasia = db.Column(db.String, unique=False)
    cnpj = db.Column(db.String, unique=False)
    cpf = db.Column(db.Integer, unique=False)
    rg = db.Column(db.Integer, unique=False)
    cep = db.Column(db.String, unique=False)
    estado = db.Column(db.String, unique=False)
    cidade = db.Column(db.String, unique=False)
    bairro = db.Column(db.String, unique=False)
    rua = db.Column(db.String, unique=False)
    nuCasa = db.Column(db.Integer, unique=False)
    complemento = db.Column(db.String, unique=False)
    foto = db.Column(db.String, unique=False, default="profile.jpg")
    data_criado = db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.needs_refresh_message_category = "Longin_Erro"
login_manager.login_message = "Faça o seu LOGIN"


def nome_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.status == "BLOQUEADO":
            flash("Usuário bloqueado", "Longin_Erro")
            return redirect(url_for("login"))
        if current_user.nivel != session.get('nivel_nome'):
            flash("Faça o login novamente.", "Longin_Erro")
            return redirect(url_for("login"))
        if current_user.is_authenticated and current_user.nome == "" or current_user.apelido == ""or current_user.fone == ""or current_user.email == ""or current_user.niver == "" or current_user.cpf == ""or current_user.rg == ""or current_user.cep == ""or current_user.estado == ""or current_user.cidade == ""or current_user.bairro == ""or current_user.rua == ""or current_user.nuCasa == "":
            flash("Finalize o seu Cadastro Primeiro", "cor-alerta")
            return redirect(url_for("atulizUser", id=current_user.id))
        return f(*args, **kwargs)

    return decorated_function


def verificacao_nivel(nivel_permitido):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("nivel") is None or session["nivel"] >= nivel_permitido:
                return f(*args, **kwargs)
            else:
                MSG = f"Você não tem permissão para acessar esta página"
                return render_template("pagina_erro.html", MSG=MSG)

        return decorated_function

    return decorator


bcrypt = Bcrypt(app)

app.config["UPLOADED_PHOTOS_DEST"] = os.path.join(basedir, "static/imagens")

photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)

migrate = Migrate(app, db)

#Configurção de aparencia

json_file_path = os.path.join(basedir, "config.json")

if not os.path.exists(json_file_path):
    # Configuração do banco de dados
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "BancoOficina.db")

    # Outras configurações que você pode querer incluir
    app.config["DEBUG"] = True

    # Cria um dicionário com as configurações
    config_data = {
        "cores": {
            "principal_botao": "#8f0000",
            "principal_principal": "#9e0000",
            "principal_secundaria": "linear-gradient(to bottom right, rgb(124, 45, 45), rgb(84, 5, 5), rgb(124, 45, 45))",
            "principal_letras": "#fffafa",
            "meschagem": 0.5
        },
        "fontes": {
            "fonte_principal": "'Palatino Linotype', 'Book Antiqua', Palatino, serif"
        },
        "icones": {
            "img_cor": 77
        }
    }

    # Cria o arquivo JSON com as configurações
    with open(json_file_path, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)


def load_config():
    basedir = os.path.abspath(os.path.dirname(__file__))

    json_file_path = os.path.join(basedir, "config.json")

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            config_data = json.load(json_file)
            return config_data
    else:
        return None
    
def save_config(config_data):
    with open(json_file_path, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)

#login com google
appConf = {
    "OAUTH2_CLIENT_ID": "943187498833-217ssj25krrvuf955e43f3mo7l8nrhl5.apps.googleusercontent.com",
    "OAUTH2_CLIENT_SECRET": "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",
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": "46701c8c-dc3b-45cc-8865-77575e81594b",
    "FLASK_PORT": 5000
}

app.secret_key = appConf.get("FLASK_SECRET")

oauth = OAuth(app)

oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",
    },
    server_metadata_url=f'{appConf.get("OAUTH2_META_URL")}',
)

ajustes()
