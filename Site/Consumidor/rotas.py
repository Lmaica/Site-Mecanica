from Site import (
    app,
    db,
    bcrypt,
    photos,
    nome_required,
    verificacao_nivel,
    load_config,
    save_config,
    oauth,
)
from flask import (
    render_template,
    session,
    request,
    url_for,
    flash,
    redirect,
    jsonify,
    current_app,
    make_response,
    send_from_directory,
)

from Site.Carros.modelos import Carro
from Site.Clientes.modelos import Cliente
from Site.Clientes.formularios import ForCliente
import random
import string
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Site.Combo.modelos import Combo
import json
from Site.Pecas.modelos import Peca
from Site.MaoObra.modelos import Maoobra
from sqlalchemy import desc, and_, or_
import os
import secrets
from Site.Global.fun_global import Calculos_gloabal, Redutor_codigo, Edit_global
from datetime import datetime, timedelta,time
from Site.Admin.modelos import Lembretestodos
from Site.Admin.formularios import RegistrationForm, LoginFormulario, LembretesMensagens, AlterarSenhaForm
from .formularios import EmailConsumidor, CriarConsumidor
from .modelos import Token
import requests
import re
from Site.Servicos.modelos import Serviso
from functools import wraps

def verifica_cliente_ativo(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if 'id' in kwargs:
            id_conferi = kwargs['id']
            email_conferi = session.get('email_consumidor')
            session['next_url'] = request.path
            print(request.path)
            print(session['next_url'])
            cliente = Cliente.query.filter_by(email=email_conferi).first()
            if id_conferi != cliente.id:
                return redirect(url_for("Consumidor"))
            if cliente.statu == 'ATIVO':
                return f(*args, **kwargs)
            else:
                session.pop("id_consumidor", None)
                session.pop("consumidor", None)
                session.pop("email_consumidor", None)
                flash("Cadastro bloqueado.", "Longin_Erro_Utrapado")
                return redirect(url_for("loginCliente"))
        return redirect(url_for("loginCliente"))
    return decorator
        
def verificar_formato_numero(numero):
    padrao = r'^\(\d{2}\) \d{5}-\d{3,4}$'
    
    if re.match(padrao, numero):
       return False
    else:
        return True

def verificar_tentativas_login():
    if 'tentativas_login' not in session:
        session['tentativas_login'] = 0

    return session['tentativas_login'] >= 5

@app.route("/")
def Consumidor():

    page = request.args.get("page", 1, type=int)
    combos = Combo.query.filter_by(atividade='Ativo').order_by(Combo.id.desc()).paginate(page=page, per_page=10)
    combosOfertas = Combo.query.filter(Combo.status == 'Oferta', Combo.atividade == 'Ativo').order_by(Combo.id.desc())
    return render_template(
        "Consumidor/index.html",
        contentConsumidor=True,
        combosOfertas=combosOfertas,
        combos=combos,
    )

@app.route("/searchConsumidor", methods=["GET", "POST"])
def searchConsumidor():
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            busca = search_value = form["search_string"]
            search_terms = search.split()  
            nova_palavra = "Ativo"
            search_terms += [nova_palavra]
            conditions = []
            for term in search_terms:
                conditions.append(
                    or_(
                        Combo.nome.like(f'%{term}%'), 
                        Combo.atividade.like(f'%{term}%'),
                        Combo.status.like(f'%{term}%'),
                        Combo.carro.like(f'%{term}%'),
                        Combo.tipo.like(f'%{term}%'),
                        Combo.peca_os_combo.like(f'%{term}%'),
                        Combo.mo_os_combo.like(f'%{term}%'),
                        Combo.obs.like(f'%{term}%'),
                    )
                )
            get_combos = (
                    Combo.query.filter(
                        *conditions
                    )
                    .order_by(Combo.id.desc())
                    .paginate(page=page, per_page=10)
                )

            combosOfertas = Combo.query.filter(and_(Combo.status == 'Oferta', Combo.atividade == 'Ativo')).order_by(Combo.id)
            return render_template(
                "Consumidor/index.html",
                contentConsumidor=True,
                combos=get_combos,
                busca=busca,
                combosOfertas=combosOfertas,
            )
    except Exception as erro:
        MSG = f"Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

@app.route("/dadosInformativos/<int:id>", methods=["GET", "POST"])
def dadosInformativos(id):
    get_combo = Combo.query.get_or_404(id)

    peca_os = json.loads(get_combo.peca_os_combo)
    getPecas = Peca.query.order_by(Peca.id).all()
    mo_os = json.loads(get_combo.mo_os_combo)
    get_MDO = Maoobra.query.order_by(Maoobra.id).all()
    marcas = Edit_global.remove_repetidos(
        [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
    )
    items_data_pecas = []
    soma_pagos = []
    soma_pecas = []
    soma_total = []
    if "itens" in peca_os:
        for item in peca_os["itens"]:
            peca_id = item.get("peca_id")
            un = item.get("un")
            peca_nome = item.get("peca_nome")
            lado = item.get("lado")
            valor_final = item.get("valor_final")
            peca_codigo = item.get("peca_codigo")
            valor_custo = item.get("valor_custo")
            if peca_id is not None:
                if len(getPecas) == 0:
                    Pagosoma = Calculos_gloabal.valor_para_Calculos(
                        valor_custo
                    ) * int(un)
                    PagoFor = Calculos_gloabal.format_valor_moeda(Pagosoma)
                    soma_pagos.append(Pagosoma)
                    somar_dados_uni = Calculos_gloabal.valor_para_Calculos(valor_final)
                    soma_do_valor = int(un) * somar_dados_uni
                    soma_pecas.append(soma_do_valor)
                    soma_total.append(soma_do_valor)
                    soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                    items_data_pecas.append(
                        {
                            "codigo": peca_codigo,
                            "nome": peca_nome,
                            "preso": valor_final,
                            "pago_total": soma_formarmatado,
                            "pago": PagoFor,
                            "un": un,
                            "lado": lado,
                        }
                    )
                else:
                    peca_encontrada = False
                    for getPeca in getPecas:
                        if getPeca.id == peca_id:
                            peca_encontrada = True
                            Pagosoma = Calculos_gloabal.valor_para_Calculos(
                                getPeca.pago
                            ) * int(un)
                            PagoFor = Calculos_gloabal.format_valor_moeda(Pagosoma)
                            soma_pagos.append(Pagosoma)
                            if get_combo.status != "Orçamento":
                                somar_dados_uni = Calculos_gloabal.valor_para_Calculos(valor_final)
                                soma_do_valor = int(un) * somar_dados_uni
                                soma_pecas.append(soma_do_valor)
                                soma_total.append(soma_do_valor)
                                soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                                items_data_pecas.append(
                                    {
                                        "codigo": peca_codigo,
                                        "nome": peca_nome,
                                        "preso": valor_final,
                                        "pago_total": soma_formarmatado,
                                        "pago": PagoFor,
                                        "un": un,
                                        "lado": lado,
                                    }
                                )
                            else:
                                somar_dados_uni = Calculos_gloabal.valor_para_Calculos(getPeca.preso)
                                soma_do_valor = int(un) * somar_dados_uni
                                soma_pecas.append(soma_do_valor)
                                soma_total.append(soma_do_valor)
                                soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                                items_data_pecas.append(
                                    {
                                        "codigo": getPeca.codigo,
                                        "nome": getPeca.nome,
                                        "preso": getPeca.preso,
                                        "pago_total": soma_formarmatado,
                                        "pago": PagoFor,
                                        "un": un,
                                        "lado": lado,
                                    }
                                )
                    if not peca_encontrada:
                        Pagosoma = Calculos_gloabal.valor_para_Calculos(
                            valor_custo
                        ) * int(un)
                        PagoFor = Calculos_gloabal.format_valor_moeda(Pagosoma)
                        somar_dados_uni = Calculos_gloabal.valor_para_Calculos(valor_final)
                        soma_do_valor = int(un) * somar_dados_uni
                        soma_pecas.append(soma_do_valor)
                        soma_total.append(soma_do_valor)
                        soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                        items_data_pecas.append(
                            {
                                "codigo": peca_codigo,
                                "nome": peca_nome,
                                "preso": valor_final,
                                "pago_total": soma_formarmatado,
                                "pago": PagoFor,
                                "un": un,
                                "lado": lado,
                            }
                        )
    items_data_MDO = []
    if "itens" in mo_os:
        for item_MDO in mo_os["itens"]:
            mo_id = item_MDO.get("MDO_id")
            mo_preso = item_MDO.get("MDO_preso")
            mo_nome = item_MDO.get("MDO_nome")
            if mo_id is not None:
                if len(get_MDO) == 0:
                    mdo_valor_para_soma = Calculos_gloabal.valor_para_Calculos(mo_preso)
                    soma_total.append(mdo_valor_para_soma)
                    items_data_MDO.append(
                        {
                            "nome": mo_nome,
                            "preso": mo_preso,
                        }
                    )
                else:
                    encontrado = False
                    for getmo in get_MDO:
                        if getmo.id == mo_id:
                            encontrado = True
                            if get_combo.status != "Orçamento":
                                mdo_valor_para_soma = Calculos_gloabal.valor_para_Calculos(mo_preso)
                                soma_total.append(mdo_valor_para_soma)
                                items_data_MDO.append(
                                    {
                                        "nome": mo_nome,
                                        "preso": mo_preso,
                                    }
                                )
                            else:
                                mdo_valor_para_soma = Calculos_gloabal.valor_para_Calculos(getmo.preso)
                                soma_total.append(mdo_valor_para_soma)
                                items_data_MDO.append(
                                    {
                                        "nome": getmo.nomemaoobra.nome,
                                        "preso": getmo.preso,
                                    }
                                )
                            break
                    
                    if not encontrado:
                        mdo_valor_para_soma = Calculos_gloabal.valor_para_Calculos(mo_preso)
                        soma_total.append(mdo_valor_para_soma)
                        items_data_MDO.append(
                            {
                                "nome": mo_nome,
                                "preso": mo_preso,
                            }
                        )
    similar_combos_compatibles = Combo.query.filter(
        or_(Combo.nome == get_combo.nome),
        Combo.id != get_combo.id,
        Combo.atividade == 'Ativo'
    ).all()

    # Em seguida, buscamos os registros incompatíveis com o nome
    similar_combos_incompatibles = Combo.query.filter(
        Combo.nome != get_combo.nome,
        Combo.id != get_combo.id,
        Combo.atividade == 'Ativo'
    ).all()

    # Concatenamos os resultados
    similar_combos = similar_combos_compatibles + similar_combos_incompatibles

    # Limitamos o resultado final a apenas 5 dados
    similar_combos = similar_combos[:5]
    return render_template(
        "/Consumidor/abrirItensConsumidor.html",
        contentConsumidor=True,
        Combo=get_combo,
        similarCombos=similar_combos,
        items_data_pecas=items_data_pecas,
        items_data_MDO=items_data_MDO,
        marcas=marcas,
    )

@app.route("/pedidoContato", methods=["PUT"])
def pedidoContato():
    id_conferi = session.get('id_consumidor')
    if id_conferi:
        nome_conferi = session.get('consumidor')
        msg = "O cliente " + str(nome_conferi) + " id " + str(id_conferi) + ' Gostaria de informações.'
        data_atual = datetime.now()
        data_atual_mais_30_dias = data_atual + timedelta(days=30)
        lembrete = Lembretestodos(
            titulo='ENTRAR EM CONTATO',
            msg= msg,
            tipo='ADIVERTENCIA',
            autor='CLIENTE',
            destinatario='TODOS',
            data_inicil=data_atual,
            data_fim=data_atual_mais_30_dias,
        )
        db.session.add(lembrete)
        db.session.commit()
        flash='Entraremos em contato assim que possível.'
        
        response_data = {
            "success": True,
            "message": flash,
            "cor": "cor-ok",
        }
        return jsonify(response_data)
    else:
        flash=False
        response_data = {
            "success": True,
            "message": flash,
            "cor": "cor-ok",
        }
        return jsonify(response_data)


#login cliente
@app.route("/loginCliente", methods=["GET", "POST"])
def loginCliente():
    form = LoginFormulario(request.form)
    if verificar_tentativas_login():
        flash('Tentativas esgotadas.Tente mais tarde.', 'Longin_Erro_Utrapado')
        return render_template("Consumidor/login.html", form=form)
    else:
        if request.method == "POST" and form.validate():
            clienteConsumidor = Cliente.query.filter_by(email=form.email.data).first()
            if clienteConsumidor:
                if clienteConsumidor.senha == None:
                    session['tentativas_login'] += 1
                    flash("E-mail ou senha inválido", "Longin_Erro_Utrapado")
                    return redirect(url_for("loginCliente"))
                else:
                    if clienteConsumidor and bcrypt.check_password_hash(clienteConsumidor.senha, form.senha.data):
                        if clienteConsumidor.statu != 'ATIVO':
                            flash("Cadastro bloqueado.", "Longin_Erro_Utrapado")
                            return redirect(url_for("loginCliente"))
                        session["id_consumidor"] = clienteConsumidor.id
                        session["consumidor"] = clienteConsumidor.nome
                        session["email_consumidor"] = clienteConsumidor.email
                        flash(f"Sejá Bem Vindo {clienteConsumidor.nome}", "cor-ok")
                        next_url = session.pop('next_url', None)
                        return redirect(next_url or url_for('Consumidor'))
                    else:
                        session['tentativas_login'] += 1
                        flash("E-mail ou senha inválido", "Longin_Erro_Utrapado")
                        return redirect(url_for("loginCliente"))
            else:
                session['tentativas_login'] += 1
                flash("E-mail ou senha inválido", "Longin_Erro_Utrapado")
                return redirect(url_for("loginCliente"))
        return render_template("Consumidor/login.html", form=form)


@app.route("/AvisoEnvio", methods=["GET", "POST"])
def AvisoEnvio():
    return render_template("Consumidor/EmailEviado.html")


@app.route("/CriarLogin", methods=["GET", "POST"])
def CriarLogin():
    form = EmailConsumidor(request.form)
    if request.method == 'POST':
        try:
            validate_email(form.email.data.strip())
            user = Cliente.query.filter_by(email=form.email.data.strip()).first()
            if form.email.data.strip() == form.confirm_email.data.strip(): 
                if user and user.senha is not None and user.senha != '':
                    flash('E-mail Já Cadastrado', 'Longin_Erro_Utrapado')
                else:
                    nova_senha = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    Redutor_codigo.enviar_email_confirmar(form.email.data.strip(), nova_senha,'CONFIRME', False)
                    get_token = Token(
                        requisitor=form.email.data.strip(),
                        token=nova_senha,
                    )
                    db.session.add(get_token)
                    db.session.commit()
                    return redirect(url_for("AvisoEnvio"))
            else:
                flash('Emails devem ser iguais.', 'Longin_Erro_Utrapado')
        except EmailNotValidError:
            flash('E-mail inválido.', 'Longin_Erro_Utrapado')
        except Exception as e:
            msg = "O Email de quem Recebeu O erro " + form.email.data.strip() + ' Erro ' + str(e)
            data_atual = datetime.now()
            data_atual_mais_30_dias = data_atual + timedelta(days=30)
            lembrete = Lembretestodos(
                titulo='Erro Ao Criar Cadastro',
                msg= msg,
                tipo='ADIVERTENCIA',
                autor='Erro',
                destinatario='TODOS',
                data_inicil=data_atual,
                data_fim=data_atual_mais_30_dias,
            )
            db.session.add(lembrete)
            db.session.commit()
            flash('Erro ao enviar o e-mail.', 'Longin_Erro_Utrapado')
    return render_template("Consumidor/EmailConfirme.html", form=form)

@app.route('/confirm/<string:usuario>/<string:token>', methods=['GET', 'POST'])
def confirm_email(usuario, token):
    try:
        user = Token.query.filter_by(requisitor=usuario, token=token).first_or_404()
        userCliente = Cliente.query.filter_by(email=usuario).first()
        if user:
            form = CriarConsumidor(request.form)
            if request.method == 'POST':
                if form.senha.data.strip() == '':
                    flash("Informe a senha.", "Longin_Erro_Utrapado")
                elif verificar_formato_numero(form.fone.data.strip()):
                    flash("Telefone invalido", "Longin_Erro_Utrapado")
                elif form.senha.data.strip() != form.confirmacao_senha.data.strip():
                    flash("As senhas não são compatíveis.", "Longin_Erro_Utrapado")
                elif form.nome.data.strip() == '':
                    flash("Informe seu nome.", "Longin_Erro_Utrapado")
                elif form.fone.data.strip() == '':
                    flash("Informe seu telefone.", "Longin_Erro_Utrapado")
                else:
                    hash_senha = bcrypt.generate_password_hash(form.senha.data.strip())
                    if userCliente and (userCliente.senha == None or userCliente.senha == ''):
                        userCliente.nome = form.nome.data.upper().strip()
                        userCliente.fone = form.fone.data.strip()
                        userCliente.email=user.requisitor
                        userCliente.senha=hash_senha
                        db.session.commit()
                        
                        db.session.delete(user)
                        db.session.commit()
                    else:
                        cadastrar = Cliente(
                            nome=form.nome.data.upper().strip(),
                            fone=form.fone.data.strip(),
                            fone1=None,
                            email=user.requisitor,
                            niver=None,
                            cpf=None,
                            rg=None,
                            razaoSocial=None,
                            nomeFantasia=None,
                            cnpj=None,
                            senha=hash_senha,
                            cep=None,
                            estado=None,
                            cidade=None,
                            bairro=None,
                            rua=None,
                            nuCasa=None,
                            complemento=None,
                            foto="foto.jpg",
                            statu='ATIVO',
                            pjoucpf=0,
                        )
                        db.session.add(cadastrar)
                        db.session.commit()
                        
                        db.session.delete(user)
                        db.session.commit()
                    flash("Faça seu login", "Longin_Erro_Utrapado")
                    return redirect(url_for("loginCliente"))
        else:
            flash("Este e-mail já foi confirmado.", "Longin_Erro_Utrapado")
            return redirect(url_for("loginCliente"))
    except:
        flash("Este e-mail já foi confirmado.", "Longin_Erro_Utrapado")
        return redirect(url_for("loginCliente"))

    return render_template("Consumidor/CriarCadastro.html", form=form)

@app.route("/user_consumidor/logaut")
def cliente_consumidor_logaut():
    session.pop("id_consumidor", None)
    session.pop("consumidor", None)
    session.pop("email_consumidor", None)

    return redirect(url_for("Consumidor"))

# Logen com google
@app.route("/Login_google_Cliente")
def Login_google_Cliente():
    user_session = session.get("user")
    if not session:
        return redirect(url_for("googleLoginClientes"))
    name = user_session.get("name")
    email = user_session.get("email")
    if email is not None:
        user = Cliente.query.filter_by(email=email).first()
    else:
        user = None
    if user:
        return redirect(url_for("googleLoginClientes"))
    else:
        cadastrar = Cliente(
            nome=name.upper().strip(),
            fone=None,
            fone1=None,
            email=email.strip(),
            niver=None,
            cpf=None,
            rg=None,
            razaoSocial=None,
            nomeFantasia=None,
            cnpj=None,
            senha=None,
            cep=None,
            estado=None,
            cidade=None,
            bairro=None,
            rua=None,
            nuCasa=None,
            complemento=None,
            foto="foto.jpg",
            statu='ATIVO',
            pjoucpf=0,
        )
        db.session.add(cadastrar)
        db.session.commit()
        return redirect(url_for("googleLoginClientes"))


@app.route("/signin-google-clientes")
def googleCallbackClientes():
    token = oauth.myApp.authorize_access_token()
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    userinfo_response = requests.get(userinfo_url, headers={
        "Authorization": f"Bearer {token['access_token']}"
    })
    userinfo_data = userinfo_response.json()

    token["name"] = userinfo_data.get("name")
    token["email"] = userinfo_data.get("email") 

    personDataUrl = "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays"
    personData = requests.get(personDataUrl, headers={
        "Authorization": f"Bearer {token['access_token']}"
    }).json()
    token["personData"] = personData
    session["user"] = token
    return redirect(url_for("Login_google_Cliente"))


@app.route("/google-login-clientes")
def googleLoginClientes():
    if "user" in session:
        user_session = session.get("user")
        emailPreAnalise = user_session.get("email")
        user = Cliente.query.filter_by(email=emailPreAnalise).first()
        if user:
            if user.statu != 'ATIVO':
                flash("Cadastro bloqueado.", "Longin_Erro_Utrapado")
                return redirect(url_for("loginCliente"))
            session["id_consumidor"] = user.id
            session["consumidor"] = user.nome
            session["email_consumidor"] = user.email
            next_url = session.pop('next_url', None)
            return redirect(next_url or url_for('Consumidor'))
        else:
            return redirect(url_for("Login_google_Cliente"))
        
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("googleCallbackClientes", _external=True))

#arrea do cliente-consumidor

@app.route("/perfilCliente/<int:id>")
@verifica_cliente_ativo
def dadosConsumidor(id):
    try:
        users = Cliente.query.get_or_404(id)
        page = request.args.get("page", 1, type=int)
        servisos = (Serviso.query.filter(Serviso.cliente_os == users)
            .filter(Serviso.status == "Finalizado")
            .filter(
                Serviso.id != 0
            ) 
            .order_by(Serviso.data_finalizada.desc())
            .paginate(page=page, per_page=10)
        )
        if servisos.items:
            pass
        else:
            servisos=False

        servisos_atual = (Serviso.query.filter(Serviso.cliente_os == users)
            .filter(Serviso.status == "Aprovado")
            .filter(
                Serviso.id != 0
            ) 
            .order_by(Serviso.data_finalizada.desc())
        )
        if servisos_atual.count() > 0:
            pass
        else:
            servisos_atual=False
        return render_template("Consumidor/dadosConsumidor.html", user=users,contentConsumidor=True,servisos=servisos,servisos_atual=servisos_atual)
    except Exception as erro:
        msg = "O Ususario id " + str(id) + ' Erro não compativel' + str(erro)
        data_atual = datetime.now()
        data_atual_mais_30_dias = data_atual + timedelta(days=30)
        lembrete = Lembretestodos(
            titulo='erro Ao entrar dos Dados',
            msg= msg,
            tipo='ADIVERTENCIA',
            autor='Erro',
            destinatario='TODOS',
            data_inicil=data_atual,
            data_fim=data_atual_mais_30_dias,
        )
        db.session.add(lembrete)
        db.session.commit()
        MSG = f"Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
        
    
@app.route("/atualizar-cadastro/<int:id>", methods=["GET", "POST"])
@verifica_cliente_ativo
def atualizarCadastroCli(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        id_conferi = session.get('email_consumidor')
        if id_conferi != cliente.email:
            MSG = f"Favor, evite usar a barra de pesquisa para navegar no Site."
            return render_template("pagina_erro.html", MSG=MSG)
        form = ForCliente(request.form)
        if form.validate_on_submit() or request.method == 'POST':
            if request.files.get("image_1"):
                if cliente.foto != "foto.jpg":
                    try:
                        os.unlink(
                            os.path.join(
                                current_app.root_path,
                                "static/imagens/" + cliente.foto,
                            )
                        )
                        cliente.foto = photos.save(
                            request.files.get("image_1"),
                            name=secrets.token_hex(10) + "...",
                        )
                    except:
                        cliente.foto = "foto.jpg"
                else:
                    try:
                        cliente.foto = photos.save(
                            request.files.get("image_1"),
                            name=secrets.token_hex(10) + "...",
                        )
                    except:
                        cliente.foto = "foto.jpg"
            if cliente.cnpj:
               pass
            else:
               form.razaoSocial.data = ''
               form.nomeFantasia.data = ''
            cliente.nome = form.nome.data.upper().strip()
            cliente.fone = form.fone.data
            cliente.fone1 = form.fone1.data
            cliente.niver = form.niver.data
            cliente.cpf = form.cpf.data
            cliente.rg = form.rg.data
            cliente.razaoSocial = form.razaoSocial.data.upper().strip()
            cliente.nomeFantasia = form.nomeFantasia.data.upper().strip()
            cliente.cnpj = form.cnpj.data
            cliente.cep = form.cep.data
            cliente.estado = form.estado.data.upper().strip()
            cliente.cidade = form.cidade.data.upper().strip()
            cliente.bairro = form.bairro.data.upper().strip()
            cliente.rua = form.rua.data.upper().strip()
            cliente.nuCasa = form.nuCasa.data
            cliente.complemento = form.complemento.data.upper().strip()
            db.session.commit()
            flash(f"O Dados Atulizado com Sucesso!!!", "cor-ok")
            return redirect("/perfilCliente/{}".format(cliente.id))
        attributes = [
            "nome",
            "fone",
            "fone1",
            "niver",
            "cpf",
            "rg",
            "razaoSocial",
            "nomeFantasia",
            "cnpj",
            "cep",
            "estado",
            "cidade",
            "bairro",
            "rua",
            "nuCasa",
            "complemento",
        ]

        for attribute in attributes:
            getattr(form, attribute).data = getattr(cliente, attribute)
        return render_template("Consumidor/addClientes.html",contentConsumidor=True, cliente=cliente, form=form)
    except Exception as erro:
        msg = "Erro com  " + str(id) + ' Erro não compativel' + str(erro)
        data_atual = datetime.now()
        data_atual_mais_30_dias = data_atual + timedelta(days=30)
        lembrete = Lembretestodos(
            titulo='Erro ao editar',
            msg= msg,
            tipo='ADIVERTENCIA',
            autor='Erro',
            destinatario='TODOS',
            data_inicil=data_atual,
            data_fim=data_atual_mais_30_dias,
        )
        db.session.add(lembrete)
        db.session.commit()
        MSG = f"Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route('/alterarSenha/<int:id>', methods=['GET', 'POST'])
@verifica_cliente_ativo
def alterarSenhaConsumidor(id):
    users = Cliente.query.get_or_404(id)
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        hash_senha = bcrypt.generate_password_hash(form.senha_nova.data)
        users.senha = hash_senha
        db.session.commit()
        flash('Senha alterada com sucesso!', 'cor-ok')
        return redirect("/perfilCliente/{}".format(users.id))
    elif request.method == 'POST':
        flash('As senhas não coincidem. Por favor, tente novamente.', 'cor-alerta')
    return render_template('Consumidor/alterarSenha.html',contentConsumidor=True, form=form, users=users)

@app.route("/recuperarSenha", methods=["GET", "POST"])
def recuperarSenha():
    form = EmailConsumidor(request.form)
    if request.method == 'POST':
        try:
            validate_email(form.email.data.strip())
            user = Cliente.query.filter_by(email=form.email.data.strip()).first()
            if form.email.data.strip() == form.confirm_email.data.strip(): 
                if user:
                    nova_senha = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    Redutor_codigo.enviar_email_confirmar(form.email.data.strip(), nova_senha, False,False)
                    get_token = Token(
                        requisitor=form.email.data.strip(),
                        token=nova_senha,
                    )
                    db.session.add(get_token)
                    db.session.commit()
                    return redirect(url_for("AvisoEnvio"))
                else:
                    flash('E-mail Não Cadastrado', 'Longin_Erro_Utrapado')
            else:
                flash('Emails devem ser iguais.', 'Longin_Erro_Utrapado')
        except EmailNotValidError:
            flash('E-mail inválido.', 'Longin_Erro_Utrapado')
        except Exception as e:
            msg = "O Email de quem Recebeu O erro " + form.email.data.strip() + ' Erro ' + str(e)
            data_atual = datetime.now()
            data_atual_mais_30_dias = data_atual + timedelta(days=30)
            lembrete = Lembretestodos(
                titulo='Erro Ao Criar Cadastro',
                msg= msg,
                tipo='ADIVERTENCIA',
                autor='Erro',
                destinatario='TODOS',
                data_inicil=data_atual,
                data_fim=data_atual_mais_30_dias,
            )
            db.session.add(lembrete)
            db.session.commit()
            flash('Erro ao enviar o e-mail.', 'Longin_Erro_Utrapado')
    return render_template("Consumidor/EmailConfirme.html", form=form)

@app.route('/resete_senha/<string:usuario>/<string:token>', methods=['GET', 'POST'])
def resete_senha(usuario, token):
    try:
        user = Token.query.filter_by(requisitor=usuario, token=token).first_or_404()
        userCliente = Cliente.query.filter_by(email=usuario).first()
        if user and userCliente:
            form = CriarConsumidor(request.form)
            if request.method == 'POST':
                if form.senha.data.strip() == '':
                    flash("Informe a senha.", "Longin_Erro_Utrapado")
                elif form.senha.data.strip() != form.confirmacao_senha.data.strip():
                    flash("As senhas não são compatíveis.", "Longin_Erro_Utrapado")
                else:
                    hash_senha = bcrypt.generate_password_hash(form.senha.data.strip())
                    userCliente.senha=hash_senha
                    db.session.commit()

                    db.session.delete(user)
                    db.session.commit()
                    flash("Faça seu login", "Longin_Erro_Utrapado")
                    return redirect(url_for("loginCliente"))
        else:
            flash("Este link já foi usado.", "Longin_Erro_Utrapado")
            return redirect(url_for("loginCliente"))
    except:
        flash("Este link já foi usado.", "Longin_Erro_Utrapado")
        return redirect(url_for("loginCliente"))

    return render_template("Consumidor/CriarCadastro.html", form=form,redefinirSenha=True)



