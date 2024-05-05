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
)
from .formularios import RegistrationForm, LoginFormulario, LembretesMensagens, AlterarSenhaForm
from .modelos import User, Cargo, Metasliquido, Metasbruto, Lembretestodos, Metasmecanico, Metasvendedor
import secrets
import os
from Site.Global.fun_global import (
    Redutor_codigo,
    Calculos_gloabal,
)
from flask_login import login_required, current_user, login_user, logout_user
from Site.Servicos.modelos import Serviso
from datetime import datetime, timedelta 
from sqlalchemy import and_, or_, desc,func, extract,cast,Integer, Numeric
import requests
from Site.Carros.modelos import Carro
from Site.Clientes.modelos import Veiculo
from sqlalchemy.sql import text
from Site.Caixa.modelos import Caixa,Catcaixa
import random
import string
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Site.Combo.modelos import Combo
import json
from Site.Consumidor.modelos import Token

def get_results_dict(query_results, date_extractor, *value_columns):
    from collections import defaultdict
    
    results_dict = defaultdict(lambda: {col: 0 for col in value_columns})
    
    for result in query_results:
        key = tuple(getattr(result, attr) for attr in date_extractor)
        for col in value_columns:
            results_dict[key][col] += getattr(result, col) or 0
            
    for key in results_dict:
        for col in value_columns:
            results_dict[key][col] = round(results_dict[key][col], 2)
            
    sorted_results = dict(sorted(results_dict.items()))
    return sorted_results


def combine_results_dicts(main_dict, additional_dict, *keys):
    for key in keys:
        if key in main_dict and key in additional_dict:
            if isinstance(main_dict[key], dict) and isinstance(additional_dict[key], dict):
                main_dict[key].update(additional_dict[key])


def buscar_dados_dois_banco(data_objeto_data_inicio, data_objeto_data_fim, granularity):
    date_attributes = {
        'dia': ['ano', 'mes', 'dia'],
        'mes': ['ano', 'mes'],
        'ano': ['ano']
    }[granularity]
    resultados = (
        db.session.query(
            cast(func.strftime('%Y', Serviso.data_finalizada), Integer).label('ano'),
            cast(func.strftime('%m', Serviso.data_finalizada), Integer).label('mes'),
            cast(func.strftime('%d', Serviso.data_finalizada), Integer).label('dia'),
            func.sum(text("CAST(REPLACE(REPLACE(REPLACE(REPLACE(valor_pesas, 'R$', ''),'\xa0', ''), '.', ''), ',', '.') AS FLOAT)")).label('PEÇAS'),
            func.sum(text("CAST(REPLACE(REPLACE(REPLACE(REPLACE(valor_mdo, 'R$', ''),'\xa0', ''), '.', ''), ',', '.') AS FLOAT)")).label('SERVIÇOS')
        )
        .filter(
            Serviso.data_finalizada.between(data_objeto_data_inicio, data_objeto_data_fim),
            Serviso.status == "Finalizado",
            Serviso.id != 0,
        )
        .group_by(cast(func.strftime('%Y', Serviso.data_finalizada), Integer),
                cast(func.strftime('%m', Serviso.data_finalizada), Integer),
                cast(func.strftime('%d', Serviso.data_finalizada), Integer))
        .all()
    )

    resultados_caixa = (
        db.session.query(
            cast(func.strftime('%Y', Caixa.data_criado), Integer).label('ano'),
            cast(func.strftime('%m', Caixa.data_criado), Integer).label('mes'),
            cast(func.strftime('%d', Caixa.data_criado), Integer).label('dia'),
            func.sum(text("CAST(REPLACE(REPLACE(REPLACE(REPLACE(valor, 'R$', ''), '\xa0', ''), '.', ''), ',', '.') AS FLOAT)")).label('OUTROS')
        )
        .filter(
            Caixa.data_criado.between(data_objeto_data_inicio, data_objeto_data_fim),
            Caixa.tipo == 'Entrada',
            Caixa.catcaixa_id != 1,
            Caixa.catcaixa_id != 2,
        )
        .group_by(cast(func.strftime('%Y', Caixa.data_criado), Integer),
                cast(func.strftime('%m', Caixa.data_criado), Integer),
                cast(func.strftime('%d', Caixa.data_criado), Integer))
        .all()
    )
    if resultados:
        resultados_dict = get_results_dict(resultados, date_attributes, 'SERVIÇOS', 'PEÇAS')

    if resultados_caixa:
        resultados_caixa_dict = get_results_dict(resultados_caixa, date_attributes, 'OUTROS')
  
    if resultados_caixa and resultados:
        all_dates = set(resultados_dict.keys()) | set(resultados_caixa_dict.keys())
        for date in all_dates:
            for key_dict in [resultados_dict, resultados_caixa_dict]:
                key_dict.setdefault(date, {col: 0 for col in key_dict[next(iter(key_dict))]})
        combine_results_dicts(resultados_dict, resultados_caixa_dict, *all_dates)  
    elif resultados_caixa:
        all_dates = set(resultados_caixa_dict.keys())
        for date in all_dates:
            for key_dict in [ resultados_caixa_dict]:
                key_dict.setdefault(date, {col: 0 for col in key_dict[next(iter(key_dict))]})
        resultados_dict = resultados_caixa_dict
    elif resultados:
        all_dates = set(resultados_dict.keys())
        for date in all_dates:
            for key_dict in [resultados_dict]:
                key_dict.setdefault(date, {col: 0 for col in key_dict[next(iter(key_dict))]})
    if granularity == 'dia':
        resultados_finais = sorted(
            [{'ano': date_tuple[0], 'mes': date_tuple[1], 'dia': date_tuple[2], **data} for date_tuple, data in resultados_dict.items() if len(date_tuple) == 3],
            key=lambda x: (x['ano'], x['mes'], x['dia'])
        )
    elif granularity == 'mes':
        resultados_finais = sorted(
            [{'ano': date_tuple[0], 'mes': date_tuple[1], **data} for date_tuple, data in resultados_dict.items() if len(date_tuple) == 2],
            key=lambda x: (x['ano'], x['mes'])
        )
        
    elif granularity == 'ano':
        resultados_finais = sorted(
            [{'ano': date_tuple[0], **data} for date_tuple, data in resultados_dict.items() if len(date_tuple) == 1],
            key=lambda x: (x['ano'])
        )
    return resultados_finais


def buscar_dados_banco(data_objeto_data_inicio, data_objeto_data_fim,categorias_lista, granularity,tabela):
    resultados_organizados = {}

    for index, categoria in enumerate(categorias_lista):
        if tabela == 'Tabela_Caixa':
            resultado_categoria = (
                db.session.query(
                    cast(func.strftime('%Y', Caixa.data_criado), Integer).label('ano'),
                    cast(func.strftime('%m', Caixa.data_criado), Integer).label('mes'),
                    cast(func.strftime('%d', Caixa.data_criado), Integer).label('dia'), 
                    func.sum(
                        text("CAST(REPLACE(REPLACE(REPLACE(REPLACE(valor, 'R$', ''), '\xa0', ''), '.', ''), ',', '.') AS FLOAT)")
                    ).label(categoria),
                )
                .filter(
                    Caixa.data_criado.between(data_objeto_data_inicio, data_objeto_data_fim),
                    Caixa.tipo == 'Saida',
                    Caixa.catcaixa_id != 1,
                    Caixa.catcaixa_id != 2,
                    Caixa.catcaixa.has(Catcaixa.nome == categoria)
                )
                .group_by(
                    cast(func.strftime('%Y', Caixa.data_criado), Integer),
                    cast(func.strftime('%m', Caixa.data_criado), Integer),
                    cast(func.strftime('%d', Caixa.data_criado), Integer),
                )
                .all()
            )
        else:
            resultado_categoria = (
                db.session.query(
                    cast(func.strftime('%Y', Serviso.data_finalizada), Integer).label('ano'),
                    cast(func.strftime('%m', Serviso.data_finalizada), Integer).label('mes'),
                    cast(func.strftime('%d', Serviso.data_finalizada), Integer).label('dia'),
                    func.sum(text("CAST(REPLACE(REPLACE(REPLACE(REPLACE(valor_ganho, 'R$', ''),'\xa0', ''), '.', ''), ',', '.') AS FLOAT)")).label(categoria)
                )
                .filter(
                    Serviso.data_finalizada.between(data_objeto_data_inicio, data_objeto_data_fim),
                    Serviso.status == "Finalizado",
                    Serviso.id != 0,
                )
                .group_by(cast(func.strftime('%Y', Serviso.data_finalizada), Integer),
                        cast(func.strftime('%m', Serviso.data_finalizada), Integer),
                        cast(func.strftime('%d', Serviso.data_finalizada), Integer))
                .all()
            )
        
        for resultado in resultado_categoria:
            ano, mes, dia, valor = resultado[:4]
            if granularity == 'ano':
                chave = (ano,)
            elif granularity == 'mes':
                chave = (ano, mes)
            else:
                chave = (ano, mes, dia)

            if chave not in resultados_organizados:
                resultados_organizados[chave] = {}

            valor_tratado = valor if valor is not None else 0
            resultados_organizados[chave][categoria] = valor_tratado   
    for chave, valores_categoria in resultados_organizados.items():
        for categoria in categorias_lista:
            if categoria not in valores_categoria:
                resultados_organizados[chave][categoria] = 0
    if granularity == 'dia':
        resultados_finais = sorted(
            [{'ano': date_tuple[0], 'mes': date_tuple[1], 'dia': date_tuple[2], **data} for date_tuple, data in resultados_organizados.items() if len(date_tuple) == 3],
            key=lambda x: (x['ano'], x['mes'], x['dia'])
        )
    elif granularity == 'mes':
        resultados_finais = sorted(
            [{'ano': date_tuple[0], 'mes': date_tuple[1], **data} for date_tuple, data in resultados_organizados.items() if len(date_tuple) == 2],
            key=lambda x: (x['ano'], x['mes'])
        )
    elif granularity == 'ano':
        resultados_finais = sorted(
            [{'ano': date_tuple[0], **data} for date_tuple, data in resultados_organizados.items() if len(date_tuple) == 1],
            key=lambda x: (x['ano'])
        )
    
    return resultados_finais



@app.route("/MaicaATLJ")
@login_required
@nome_required
def Admin():
    user = current_user

    data_atual = datetime.now()

    # Limpando lembretes expirados
    Lembretestodos.query.filter(
        Lembretestodos.data_fim < data_atual
    ).delete()

    # Limpando serviços antigos
    data_limite_servicos = data_atual - timedelta(days=5*365)
    Serviso.query.filter(
        Serviso.data_finalizada <= data_limite_servicos
    ).delete()

    # Resetando combos não válidos
    Combo.query.filter(
        ~(
            Combo.peca_os_combo.like('%"itens"%') |  # Alterando para pipe (|) para operador OR
            Combo.mo_os_combo.like('%"itens"%')
        ) | (Combo.nome == '') | (Combo.obs == '') | (Combo.carro == '""') |  # Usando parênteses para agrupar as condições
        (Combo.image_1 == 'foto.jpg') | (Combo.data_inicil_combo >= data_atual) |  # Usando parênteses para agrupar as condições
        ((Combo.data_final_combo != None) & (Combo.data_final_combo <= data_atual))  # Usando parênteses para agrupar as condições e alterando para != para verificar se não é None
    ).update({'atividade': None})

    # Committing changes
    db.session.commit()

    # Consulta lembretes e adivertencias
    lembretes = Lembretestodos.query.filter(
        or_(
            Lembretestodos.destinatario == "TODOS",
            Lembretestodos.destinatario == user.cargo.nome,
            Lembretestodos.destinatario == user.apelido,
        ),
        Lembretestodos.tipo == "AVISO",
    ).order_by(Lembretestodos.data_inicil.desc())

    adivertencias = Lembretestodos.query.filter(
        or_(
            Lembretestodos.destinatario == "TODOS",
            Lembretestodos.destinatario == user.cargo.nome,
            Lembretestodos.destinatario == user.apelido,
        ),
        Lembretestodos.tipo == "ADIVERTENCIA",
    ).order_by(Lembretestodos.data_inicil.desc())
    
    limite = data_atual - timedelta(hours=24)

    db.session.query(Token).filter(Token.data <= limite).delete()

    db.session.commit()
    return render_template(
        "Admin/index.html",
        lembretes=lembretes,
        adivertencias=adivertencias,
        teste='Teste valor em Pagina',
    )

@app.route('/cartaoVisita')
def cartaoVisita():
    dados = session
    agora = datetime.now()
    msg = "Acesso session " + str(dados) + " hora do Acesso " + str(agora)
    data_atual = datetime.now()
    data_atual_mais_30_dias = data_atual + timedelta(days=30)
    lembrete = Lembretestodos(
        titulo='Acesso pelo QR CODE',
        msg= msg,
        tipo='ADIVERTENCIA',
        autor='PLACA',
        destinatario='TODOS',
        data_inicil=data_atual,
        data_fim=data_atual_mais_30_dias,
    )
    db.session.add(lembrete)
    db.session.commit()
    return redirect(url_for("Consumidor"))

# Configuração de estilo
@app.route('/salvar_config', methods=['POST'])
@login_required
@nome_required
@verificacao_nivel(4)
def salvar_config():
    dados = request.get_json()
    save_config(dados)
    return redirect(url_for("Admin"))   

@app.route("/configurar")
@login_required
@nome_required
@verificacao_nivel(6)
def configurar():
    config = load_config()
    return render_template("Admin/configure.html",cores=config['cores'], fontes=config['fontes'], icones=config['icones'])

@app.route('/dados_cofigurarar', methods=['POST'])
def dados_cofigurarar():
    config = load_config()
    return config

# relatorios

@app.route("/relatorio")
@login_required
@nome_required
@verificacao_nivel(2)
def relatorio():
    return render_template("Admin/relatorios.html")


@app.route("/pagina_graficos/<string:estilo_data>/<string:tipo>")
@login_required
@nome_required
@verificacao_nivel(4)
def pagina_graficos(estilo_data,tipo):
    return render_template("Admin/pagina_gaficos.html",estilo_data=estilo_data,tipo=tipo)


@app.route('/buscar_graficos')
def buscar_graficos():
    estilo_data = request.args.get('estilo_data')
    tipo = request.args.get('tipo')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    if len(data_inicio) == 10:
        data_objeto_data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        data_objeto_data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
    else:
        data_inicio=int(data_inicio)
        data_fim=int(data_fim)
        data_objeto_data_inicio =  datetime(data_inicio,1,1,0,0,0)
        data_objeto_data_fim = datetime(data_fim,12,31,0,0,0)

    data_objeto_data_fim = data_objeto_data_fim + timedelta(days=1)
    
    diferenca_meses = (data_objeto_data_fim.year - data_objeto_data_inicio.year) * 12 + (data_objeto_data_fim.month - data_objeto_data_inicio.month)
    diferenca_dias = data_objeto_data_fim.day - data_objeto_data_inicio.day
    
    if diferenca_dias > 0:
        diferenca_meses += 1
    if tipo == 'ganho':
        categorias = ['SERVIÇOS', 'PEÇAS', 'OUTROS']
    else:
        categorias = [] 
        lista_catcaixa = Catcaixa.query.filter(Catcaixa.id != 1).all()
        for catcaixa in lista_catcaixa:
            categorias.append(catcaixa.nome)

    meses_em_portugues = {
        1: 'janeiro',2: 'fevereiro',3: 'março',4: 'abril',5: 'maio',6: 'junho',
        7: 'julho',8: 'agosto',9: 'setembro',10: 'outubro',11: 'novembro',12: 'dezembro'
    }

    meses_referente= []
    if tipo == 'ganho':
        resultados_finais = buscar_dados_dois_banco(data_objeto_data_inicio, data_objeto_data_fim, estilo_data)
    else:    
        resultados_finais = buscar_dados_banco(data_objeto_data_inicio, data_objeto_data_fim,categorias, estilo_data,'Tabela_Caixa')


    excluidas = ['ano', 'mes', 'dia']
    categoria_filtradas = list({chave for item in resultados_finais for chave, valor in item.items() if chave not in excluidas})


    dados_grafico = {categoria: {} for categoria in categoria_filtradas}
    listas_categorias = {categoria: [] for categoria in categoria_filtradas}
    grafico_data = {
        'categories': meses_referente,
        'series': []
    }

    for categoria in categoria_filtradas:
        lista_categoria = []
        dados_categoria = {categoria: []}
        for resultado in resultados_finais:
            ano = resultado['ano']
            
            if estilo_data == 'dia':
                dia = resultado['dia']
                mes = resultado['mes']
                nome_mes = meses_em_portugues[mes]
                nome = str(dia) + '/' + nome_mes + '/' + str(ano)
            elif estilo_data == 'mes':
                mes = resultado['mes']
                nome_mes = meses_em_portugues[mes]
                nome = nome_mes + '/' + str(ano)
            else:
                nome = str(ano)
            meses_referente.append(nome)
            valor_categoria = resultado[f'{categoria}']
            
            
            lista_categoria.append(valor_categoria)
            dados_categoria[categoria].append(valor_categoria)

        listas_categorias[categoria] = lista_categoria
        dados_grafico[categoria] = dados_categoria

        meses_referente = list(set(meses_referente))
    for categoria in categoria_filtradas:
        for nome_serie, valores in dados_grafico[categoria].items():
            grafico_data['series'].append({'name': nome_serie, 'values': valores})

    total_somas_pizza = [sum(listas_categorias[categoria]) for categoria in categoria_filtradas]

    #para o grafico de velocidade ---------------------------------------------    
    valor_metas_liquida = Metasliquido.query.order_by(desc(Metasliquido.id)).first()
    meta_liquiudo = Calculos_gloabal.valor_para_Calculos(valor_metas_liquida.meta)
    bonos_liquiudo = Calculos_gloabal.valor_para_Calculos(valor_metas_liquida.bonos)

    if diferenca_meses > 1:
        meta_liquiudo= meta_liquiudo * diferenca_meses
        bonos_liquiudo= bonos_liquiudo * diferenca_meses

    total_mes_liquido = (
        db.session.query(
            func.sum(text("CAST(REPLACE(REPLACE(REPLACE(REPLACE(valor_ganho, 'R$', ''),'\xa0', ''), '.', ''), ',', '.') AS FLOAT)")).label('valor')
        )
        .filter(
            Serviso.data_finalizada.between(data_objeto_data_inicio, data_objeto_data_fim),
            Serviso.status == "Finalizado",
            Serviso.id != 0,
        )
        .group_by(cast(func.strftime('%Y', Serviso.data_finalizada), Integer),
                cast(func.strftime('%m', Serviso.data_finalizada), Integer),
                cast(func.strftime('%d', Serviso.data_finalizada), Integer))
        .all()
    )

    total_mes_liquido_outros = (
        db.session.query(
            func.sum(text("CAST(REPLACE(REPLACE(REPLACE(REPLACE(valor, 'R$', ''), '\xa0', ''), '.', ''), ',', '.') AS FLOAT)")).label('outros')
        )
        .filter(
            Caixa.data_criado.between(data_objeto_data_inicio, data_objeto_data_fim),
            Caixa.tipo == 'Entrada',
            Caixa.catcaixa_id != 1,
            Caixa.catcaixa_id != 2,
        )
        .group_by(cast(func.strftime('%Y', Caixa.data_criado), Integer),
                cast(func.strftime('%m', Caixa.data_criado), Integer),
                cast(func.strftime('%d', Caixa.data_criado), Integer))
        .all()
    )

    valor_total_mes_liquido = []
    for valor in total_mes_liquido:
        valor_total_mes_liquido.append(valor[0])
    valor_total_mes_liquido= sum(valor_total_mes_liquido)
    valor_total_mes_liquido_outros = []
    for valor in total_mes_liquido_outros:
        valor_total_mes_liquido_outros.append(valor[0])
    valor_total_mes_liquido_outros= sum(valor_total_mes_liquido_outros)
    
    grafico = valor_total_mes_liquido + valor_total_mes_liquido_outros
    nova_serie = {'name': 'TOTAL', 'values': []}

    for i in range(len(grafico_data['categories'])):
        soma_dia = 0
        for serie in grafico_data['series']:
            soma_dia += serie['values'][i]
        
        nova_serie['values'].append(soma_dia)

    grafico_data['series'].append(nova_serie)

    #Dados de grafico
    dados = {
            'speed_data': {
                'value': grafico,
                'meta': meta_liquiudo,
                'bonos': bonos_liquiudo
            },

            'pie_data' : {
                'categories': categoria_filtradas,
                'values': total_somas_pizza
            },

            'bar_data': grafico_data,
        }
    
    return jsonify(dados)


def verificar_tentativas_login():
    if 'tentativas_login' not in session:
        session['tentativas_login'] = 0

    return session['tentativas_login'] >= 5

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        form = LoginFormulario(request.form)
        if verificar_tentativas_login():
            flash('Tentativas esgotadas.Tente mais tarde.', 'Longin_Erro_Utrapado')
            return render_template("Admin/login.html", form=form)
        else:
            if request.method == "POST" and form.validate():
                user = User.query.filter_by(email=form.email.data).first()
                empresa = User.query.get(1)
                if user and bcrypt.check_password_hash(user.senha, form.senha.data):
                    niveis = {
                        "DONO": 6,
                        "PERITO": 5,
                        "ESPECIALISTA": 4,
                        "COMPETENTE": 3,
                        "INEXPERIENTE": 2,
                        "NOVATO": 1,
                    }
                    nivel = niveis.get(user.nivel, 0)
                    session["nome"] = user.nome
                    session["apelido"] = user.apelido
                    session["email"] = user.email
                    session["cargo"] = user.cargo.nome
                    session["nivel"] = nivel
                    session["nivel_nome"] = user.nivel
                    endereço = str(empresa.estado) + '-' + str(empresa.cidade).capitalize() + '- Bairro:' + str(empresa.bairro).capitalize() + '- Rua:' + str(empresa.rua).capitalize() + '- N:' + str(empresa.nuCasa)
                    session['dados_empresa_nome'] = empresa.nomeFantasia
                    session['dados_empresa_fone'] = empresa.fone
                    session['dados_empresa_fone1'] = empresa.fone1
                    session['dados_empresa_email'] = empresa.email
                    session['dados_empresa_logo'] = empresa.foto
                    session['dados_empresa_endereço'] = endereço
                    session['tentativas_login'] == 0
                    login_user(user)
                    flash(f"Sejá Bem Vindo {user.apelido}", "cor-ok")
                    return redirect(url_for("Admin"))
                else:
                    session['tentativas_login'] += 1
                    flash("E-mail ou senha inválido", "Longin_Erro_Utrapado")
                    return redirect(url_for("login"))
            
            return render_template("Admin/login.html", form=form)
    except:
        session['tentativas_login'] += 1
        flash("E-mail ou senha inválido", "Longin_Erro_Utrapado")
        return redirect(url_for("login"))

@app.route("/user/logaut")
def user_logaut():
    logout_user()
    session.pop("nome", None)
    session.pop("apelido", None)
    session.pop("email", None)
    session.pop("cargo", None)
    session.pop("nivel", None)
    session.pop("nivel_nome", None)
    session.pop("dados_empresa_nome", None)
    session.pop("dados_empresa_fone", None)
    session.pop("dados_empresa_fone1", None)
    session.pop("dados_empresa_email", None)
    session.pop("dados_empresa_logo", None)
    session.pop("dados_empresa_endereço", None)
    return redirect(url_for("Admin"))

# Logen com google
@app.route("/Login_google")
def Login_google():
    try:
        user_session = session.get("user")
        if not session:
            return redirect(url_for("googleLogin"))
        name = user_session.get("name")
        email = user_session.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            return redirect(url_for("googleLogin"))
        else:
            cadastrar = User(
                nome=name.upper().strip(),
                apelido='',
                fone='',
                fone1='',
                email=email.strip(),
                niver='',
                cpf='',
                rg='',
                razaoSocial='',
                nomeFantasia='',
                cnpj='',
                senha='',
                cep='',
                estado='',
                cidade='',
                bairro='',
                rua='',
                nuCasa='',
                complemento='',
                foto='foto.jpg',
                nivel='NOVATO',
                status='ATIVO',
                cargo_id=3,
            )
            db.session.add(cadastrar)
            db.session.commit()
            return redirect(url_for("googleLogin"))
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/signin-google")
def googleCallback():
    try:
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
        return redirect(url_for("Login_google"))
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/google-login")
def googleLogin():
    try:
        if "user" in session:
            user_session = session.get("user")
            emailPreAnalise = user_session.get("email")
            user = User.query.filter_by(email=emailPreAnalise).first()
            empresa = User.query.get(1)
            if user:
                niveis = {
                    "DONO": 6,
                    "PERITO": 5,
                    "ESPECIALISTA": 4,
                    "COMPETENTE": 3,
                    "INEXPERIENTE": 2,
                    "NOVATO": 1,
                }
                nivel = niveis.get(user.nivel, 0)
                session["nome"] = user.nome
                session["apelido"] = user.apelido
                session["email"] = user.email
                session["cargo"] = user.cargo.nome
                session["nivel"] = nivel
                session["nivel_nome"] = user.nivel
                endereço = str(empresa.estado) + '-' + str(empresa.cidade).capitalize() + '- Bairro:' + str(empresa.bairro).capitalize() + '- Rua:' + str(empresa.rua).capitalize() + '- N:' + str(empresa.nuCasa)
                session['dados_empresa_nome'] = empresa.nomeFantasia
                session['dados_empresa_fone'] = empresa.fone
                session['dados_empresa_fone1'] = empresa.fone1
                session['dados_empresa_email'] = empresa.email
                session['dados_empresa_logo'] = empresa.foto
                session['dados_empresa_endereço'] = endereço
                login_user(user)
                return redirect(url_for("Admin"))
            else:
                return redirect(url_for("Login_google"))
            
        return oauth.myApp.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True))
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

#Recuperar senha

def enviar_email_senha(usuario, nova_senha):
    remetente = 'maica.contato@outlook.com'  # Insira seu e-mail do Outlook como remetente
    destinatario = usuario
    assunto = "Recuperação de Senha (por favor, exclua este email após a leitura)"
    mensagem = f"""
        <p>Olá,</p>
        <p>Sua senha foi redefinida com sucesso.</p>
        <p>Aqui estão suas novas credenciais:</p>
        <p>Nova Senha: <b>{nova_senha}</b></p>
        <p>Por favor, faça o login com suas novas credenciais e altere sua senha imediatamente.</p>
        <p>por favor, exclua este email após a leitura</p>
        <p>Atenciosamente,</p>
        <p>Equipe de Suporte</p>"""

    # Configuração do servidor SMTP da Microsoft
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    usuario_smtp = 'maica.contato@outlook.com'  
    senha_smtp = 'atljMaic@2024'  

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(mensagem, 'html'))

    # Conexão com o servidor SMTP e envio do e-mail
    with smtplib.SMTP(servidor_smtp, porta) as servidor:
        servidor.starttls()
        servidor.login(usuario_smtp, senha_smtp)
        servidor.send_message(msg)


@app.route('/recuperar_senha', methods=['POST'])
def recuperar_senha():
    if request.method == 'POST':
        usuario = request.json.get('usuario')
        try:
            validate_email(usuario)
            user = User.query.filter_by(email=usuario).first()
            if user:
                nova_senha = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                enviar_email_senha(usuario, nova_senha)
                hash_senha = bcrypt.generate_password_hash(nova_senha)
                user.senha = hash_senha
                db.session.commit()
                return jsonify({'success': True, 'message': 'O e-mail de recuperação foi enviado com sucesso. Por favor, verifique a sua pasta de spam caso não encontre na caixa de entrada.'})
            else:
                return jsonify({'success': True, 'message': 'Usuario Não Encontrado.'})
        except EmailNotValidError:
            return jsonify({'success': False, 'message': 'E-mail inválido.'})
        except:
            return jsonify({'success': False, 'message': 'Erro ao enviar o e-mail de recuperação.'})

# Dados Cargos
@app.route("/Cargos")
@login_required
@nome_required
@verificacao_nivel(5)
def Cargos():
    try:
        page = request.args.get("page", 1, type=int)
        cargos = Cargo.query.order_by(Cargo.id.desc()).paginate(page=page, per_page=10)
        return render_template(
            "/umDado.html",
            perfils=cargos,
            perfil="Cargos",
            produto="Cargo",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addCargos", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def addCargos():
    return Redutor_codigo.handle_generic_add(request, Cargo, "nome", "Cargos")


@app.route("/atulizCargos/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def atulizCargos(id):
    cargo = Cargo.query.get_or_404(id)
    if cargo.id <= 3:
        flash(f"O Cargo {cargo.nome} NÂO Pode ser Editado", "cor-cancelar")
        return redirect("/Cargos")
    return Redutor_codigo.handle_generic_update(request, Cargo, id, "nome", "Cargos")


@app.route("/deleteCargos/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def deleteCargos(id):
    cargo = Cargo.query.get_or_404(id)
    if cargo.id <= 3:
        flash(f"O Cargo {cargo.nome} NÂO Pode ser deletado", "cor-cancelar")
        return jsonify()
    return Redutor_codigo.handle_generic_delete(request, Cargo, id, "nome", "Cargos")


@app.route("/searchCargos", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def searchCargos():
    return Redutor_codigo.search_generic(Cargo, "Cargos")


# Dados Usuario
@app.route("/Users")
@login_required
@nome_required
@verificacao_nivel(5)
def Users():
    try:
        page = request.args.get("page", 1, type=int)
        user = current_user
        if user.id == 1:
            users = (
                User.query.filter(User.id != 1)
                .order_by(User.id.desc())
                .paginate(page=page, per_page=10)
            )
        else:
            users = (
                User.query.filter(User.id != 1, User.nivel != "PERITO")
                .order_by(User.id.desc())
                .paginate(page=page, per_page=10)
            )
        return render_template("Admin/Users.html", users=users)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addUser", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def addUser():
    try:
        form = RegistrationForm()
        if form.validate_on_submit():
            if form.apelido.data is not None:
                form.apelido.data = form.apelido.data.upper()
            if form.razaoSocial.data is not None:
                form.razaoSocial.data = form.razaoSocial.data.upper()
            hash_senha = bcrypt.generate_password_hash(form.email.data)
            campos_verificacao = [
                ("cpf", "O CPF {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("rg", "O RG {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("email", "O Email {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("cnpj", "O CNPJ {} Pertence ao Usuario ID {} Razão Social {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("apelido", "O Apelido {} Pertence ao Usuario ID {}!!!"),
                (
                    "razaoSocial",
                    "O Razão Social {} Pertence ao Usuario ID {} CNPJ {}!!!",
                ),
            ]

            condicao_encontrada = True
            for campo, mensagem in campos_verificacao:
                valor_campo = getattr(form, campo).data
                condicao_encontrada = Redutor_codigo.verificar_existencia(
                    User, campo, valor_campo, "0", mensagem
                )
                if not condicao_encontrada:
                    break
            if condicao_encontrada:
                try:
                    foto = photos.save(
                        request.files.get("image_1"), name=secrets.token_hex(10) + "..."
                    )
                except:
                    foto = "foto.jpg"
                razaoSocial = form.razaoSocial.data.upper().strip()
                nomeFantasia = form.nomeFantasia.data.upper().strip()
                cnpj = form.cnpj.data.strip()
                cadastrar = User(
                    nome=form.nome.data.upper().strip(),
                    apelido=form.apelido.data.upper().strip(),
                    fone=form.fone.data.strip(),
                    fone1=form.fone1.data.strip(),
                    email=form.email.data.strip(),
                    niver=form.niver.data.strip(),
                    cpf=form.cpf.data.strip(),
                    rg=form.rg.data.strip(),
                    razaoSocial=razaoSocial,
                    nomeFantasia=nomeFantasia,
                    cnpj=cnpj,
                    senha=hash_senha,
                    cep=form.cep.data.strip(),
                    estado=form.estado.data.upper().strip(),
                    cidade=form.cidade.data.upper().strip(),
                    bairro=form.bairro.data.upper().strip(),
                    rua=form.rua.data.upper().strip(),
                    nuCasa=form.nuCasa.data.strip(),
                    complemento=form.complemento.data.upper().strip(),
                    foto=foto,
                    nivel=form.nivel.data,
                    status=form.status.data,
                    cargo_id=form.cargo.data,
                )
                db.session.add(cadastrar)
                db.session.commit()
                flash(f"O Usuário, Foi Cadastrado com Sucesso!!!", "cor-ok")
                return redirect(url_for("Users"))
        elif request.method == 'POST':
            error_messages = ""
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{error}"
            flash(error_messages, 'cor-alerta')
        return render_template("/Admin/addUsers.html", form=form)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
    
@app.route('/alterar_senha/<int:id>', methods=['GET', 'POST'])
@login_required
@nome_required
def alterar_senha(id):
    users = User.query.get_or_404(id)
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        hash_senha = bcrypt.generate_password_hash(form.senha_nova.data)
        users.senha = hash_senha
        db.session.commit()
        flash('Senha alterada com sucesso!', 'cor-ok')
        return render_template("Colaborador/dadosUsuario.html", user=users)  
    elif request.method == 'POST':
        flash('As senhas não coincidem. Por favor, tente novamente.', 'cor-alerta')
    return render_template('Admin/alterarSenha.html', form=form, users=users)


@app.route("/atulizUser/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
def atulizUser(id):
    try:
        user = current_user
        users = User.query.get_or_404(id)
        if (
            user.id == users.id
            or user.nivel == "DONO"
            or user.nivel == "PERITO"
            and users.nivel != "DONO"
            and users.nivel != "PERITO"
        ):
            form = RegistrationForm(request.form)

            if form.validate_on_submit():
                if form.apelido.data is not None:
                    form.apelido.data = form.apelido.data.upper()
                if form.razaoSocial.data is not None:
                    form.razaoSocial.data = form.razaoSocial.data.upper()
                
                campos_verificacao = [
                    ("cpf", "O CPF {} Pertence ao Usuario ID {} Nome {}!!!"),
                    ("rg", "O RG {} Pertence ao Usuario ID {} Nome {}!!!"),
                    ("email", "O Email {} Pertence ao Usuario ID {} Nome {}!!!"),
                    ("cnpj", "O CNPJ {} Pertence ao Usuario ID {} Razão Social {}!!!"),
                    ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                    ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                    ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                    ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                    ("apelido", "O Apelido {} Pertence ao Usuario ID {}!!!"),
                    (
                        "razaoSocial",
                        "O Razão Social {} Pertence ao Usuario ID {} CNPJ {}!!!",
                    ),
                ]
                condicao_encontrada = True
                for campo, mensagem in campos_verificacao:
                    valor_campo = getattr(form, campo).data
                    condicao_encontrada = Redutor_codigo.verificar_existencia(
                        User, campo, valor_campo, users.id, mensagem
                    )
                    if not condicao_encontrada:
                        break
                campos_verificacao_vazio = [
                    ("nome"),
                    ("apelido"),
                    ("fone"),
                    ("email"),
                    ("niver"),
                    ("cpf"),
                    ("rg"),
                    ("cep"),
                    ("estado"),
                    ("cidade"),
                    ("bairro"),
                    ("rua"),
                    ("nuCasa"),
                ]

                condicao_encontrada_vazio = True
                for campo in campos_verificacao_vazio:
                    valor_campo = getattr(form, campo).data
                    
                    if not valor_campo:
                        flash(f"O campo {campo} está vazio!","cor-alerta")
                        condicao_encontrada_vazio = False
                        return redirect(url_for("atulizUser", id=users.id))
                if condicao_encontrada and condicao_encontrada_vazio:
                    if request.files.get("image_1"):
                        if users.foto != "foto.jpg":
                            try:
                                os.unlink(
                                    os.path.join(
                                        current_app.root_path,
                                        "static/imagens/" + users.foto,
                                    )
                                )
                                users.foto = photos.save(
                                    request.files.get("image_1"),
                                    name=secrets.token_hex(10) + "...",
                                )
                            except:
                                users.foto = "foto.jpg"
                        else:
                            try:
                                users.foto = photos.save(
                                    request.files.get("image_1"),
                                    name=secrets.token_hex(10) + "...",
                                )
                            except:
                                users.foto = "foto.jpg"
                    attributes = [
                        "nome",
                        "apelido",
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
                        "nivel",
                        "status",
                        "complemento",
                    ]

                    for attribute in attributes:
                        setattr(
                            users,
                            attribute,
                            getattr(form, attribute).data.upper().strip(),
                        )

                    users.email = form.email.data.strip()
                    if user.id == users.id == 1:
                        users.cargo_id = 1
                        users.nivel = "DONO"
                    else:
                        users.cargo_id = form.cargo.data
                    db.session.commit()
                    flash(f"Usuario, Foi Atulizado com Sucesso!!!", "cor-ok")
                    if current_user == users:
                        return render_template(
                            "Colaborador/dadosUsuario.html", user=user
                        )
                    else:
                        return redirect("/Users")
            elif request.method == 'POST':
                error_messages = ""
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages += f"{error}"
                flash(error_messages, 'cor-alerta')
            attributes = [
                "nome",
                "apelido",
                "fone",
                "fone1",
                "email",
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
                "nivel",
                "status",
                "complemento",
            ]
            for attribute in attributes:
                getattr(form, attribute).data = getattr(users, attribute)
            if user.id == users.id == 1:
                form.cargo.choices.insert(0, (2, users.cargo.nome))
                form.nivel.choices.insert(0, ("PERITO", "PERITO"))
            else:
                form.cargo.choices.insert(0, (users.cargo.id, users.cargo.nome))
            return render_template("/Admin/addUsers.html", users=users, form=form)
            
        else:
            MSG = f"Favor, {user.apelido}, evite usar a barra de pesquisa para navegar no sistema, se possível."
            return render_template("pagina_erro.html", MSG=MSG)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deleteUser/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def deleteUser(id):
    try:
        users = User.query.get_or_404(id)
        Usernome = users.nome
        if users.id == 1:
            flash(f"O User {Usernome} NÂO Pode ser deletado", "cor-cancelar")
            return jsonify()
        if request.method == "POST":
            try:
                db.session.delete(users)
                db.session.commit()
                flash(f"O User {Usernome} foi Deletada com Sucesso!!!", "cor-ok")
                try:
                    if users.foto != "foto.jpg":
                        os.remove(
                            os.path.join(
                                current_app.root_path, "static/imagens/" + users.foto
                            )
                        )
                    else:
                        pass
                except:
                    pass
                return jsonify()
            except:
                flash(
                    f"{Usernome} NÃo pode ser APAGADO, Sem Antes APAGAR os Os lembrete cadatrados",
                    "cor-alerta",
                )
            return jsonify()

        flash(f"O User {Usernome} NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchUser", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def searchUser():
    try:
        user = current_user
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "id":
                search_value = form["search_string"]
                search = "{0}".format(search_value)
                if user.id == 1:
                    Users = (
                        User.query.filter(getattr(User, escolha).like(search), User.id != 1)
                        .order_by(User.id.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    Users = (
                        User.query.filter(getattr(User, escolha).like(search), User.id != 1, User.nivel != "PERITO")
                        .order_by(User.id.desc())
                        .paginate(page=page, per_page=10)
                    )

            elif escolha == "email":
                search_va = form["search_string"]
                sear = "%{0}%".format(search_va)
                if user.id == 1:
                    Users = (
                        User.query.filter(getattr(User, escolha).like(search), User.id != 1)
                        .order_by(User.id.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    Users = (
                        User.query.filter(getattr(User, escolha).like(search), User.id != 1, User.nivel != "PERITO")
                        .order_by(User.id.desc())
                        .paginate(page=page, per_page=10)
                    )
            else:
                if user.id == 1:
                    Users = (
                        User.query.filter(getattr(User, escolha).like(search), User.id != 1)
                        .order_by(User.id.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    Users = (
                        User.query.filter(getattr(User, escolha).like(search), User.id != 1, User.nivel != "PERITO")
                        .order_by(User.id.desc())
                        .paginate(page=page, per_page=10)
                    )

            return render_template(
                "/Admin/Users.html",
                users=Users,
                busca=busca,
                escolha=escolha,
            )
        else:
            return redirect("/Users")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/dadosUsuario/<int:id>")
@login_required
@nome_required
def dadosUsuario(id):
    try:
        user = current_user
        users = User.query.get_or_404(id)
        if user.id != users.id:
            MSG = f"Favor, {user.apelido}, evite usar a barra de pesquisa para navegar no sistema, se possível."
            return render_template("pagina_erro.html", MSG=MSG)
        return render_template("Colaborador/dadosUsuario.html", user=user)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Metas E Bonos
@app.route("/MetaLiquida")
@login_required
@nome_required
@verificacao_nivel(4)
def MetaLiquida():
    try:
        page = request.args.get("page", 1, type=int)
        MetaLiquidas = Metasliquido.query.order_by(Metasliquido.id.desc()).paginate(
            page=page, per_page=10
        )
        ultimo_dado = Metasliquido.query.order_by(desc(Metasliquido.id)).first()
        return render_template(
            "/umDado.html",
            ultimo_dado=ultimo_dado,
            perfils=MetaLiquidas,
            perfil="MetaLiquida",
            produto="Valor Metas Liquida",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addMetaLiquida", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addMetaLiquida():
    try:
        if request.method == "POST":
            meta = request.form.get("meta").strip()
            bonos = request.form.get("bonos").strip()
            filtro = Metasliquido.query.order_by(desc(Metasliquido.id)).first()
            if filtro.meta == meta:
                flash(
                    f"Esse ja é o Valor Atual da Meta!!!",
                    "cor-alerta",
                )
            elif meta == 0.00:
                flash(
                    f"O Valor R$ 0,00, Não é Valido!!!",
                    "cor-alerta",
                )
            elif Calculos_gloabal.valor_para_Calculos(
                meta
            ) > Calculos_gloabal.valor_para_Calculos(bonos):
                flash(
                    f"O Valor de Bonos não pode ser menor que a Meta!!!",
                    "cor-alerta",
                )
            else:
                valores = Metasliquido(meta=meta, bonos=bonos)
                db.session.add(valores)
                flash(
                    f"O Valor Foi Atualizado com Sucesso!!!",
                    "cor-ok",
                )
                db.session.commit()
                return redirect(url_for("MetaLiquida"))
        return render_template(
            "/addUmDado.html",
            dado="",
            perfil="MetaLiquida",
            produto="Valor Metas",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/MetaBruta")
@login_required
@nome_required
@verificacao_nivel(4)
def MetaBruta():
    try:
        page = request.args.get("page", 1, type=int)
        MetaBrutas = Metasbruto.query.order_by(Metasbruto.id.desc()).paginate(
            page=page, per_page=10
        )
        ultimo_dado = Metasbruto.query.order_by(desc(Metasbruto.id)).first()
        return render_template(
            "/umDado.html",
            ultimo_dado=ultimo_dado,
            perfils=MetaBrutas,
            perfil="MetaBruta",
            produto="Valor Metas Brunta",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addMetaBruta", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addMetaBruta():
    try:
        if request.method == "POST":
            meta = request.form.get("meta").strip()
            bonos = request.form.get("bonos").strip()
            filtro = Metasbruto.query.order_by(desc(Metasbruto.id)).first()
            if filtro.meta == MetaBruta:
                flash(
                    f"Esse ja é o Valor Atual da Meta!!!",
                    "cor-alerta",
                )
            elif meta == 0.00:
                flash(
                    f"O Valor R$ 0,00, Não é Valido!!!",
                    "cor-alerta",
                )
            elif Calculos_gloabal.valor_para_Calculos(
                meta
            ) > Calculos_gloabal.valor_para_Calculos(bonos):
                flash(
                    f"O Valor de Bonos não pode ser menor que a Meta!!!",
                    "cor-alerta",
                )
            else:
                valores = Metasbruto(meta=meta, bonos=bonos)
                db.session.add(valores)
                flash(
                    f"O Valor Foi Atualizado com Sucesso!!!",
                    "cor-ok",
                )
                db.session.commit()
                return redirect(url_for("MetaBruta"))
        return render_template(
            "/addUmDado.html",
            dado="",
            perfil="MetaBruta",
            produto="Valor Metas",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/MetaMecanico")
@login_required
@nome_required
@verificacao_nivel(4)
def MetaMecanico():
    try:
        page = request.args.get("page", 1, type=int)
        MetaMecanicos = Metasmecanico.query.order_by(Metasmecanico.id.desc()).paginate(
            page=page, per_page=10
        )
        ultimo_dado = Metasmecanico.query.order_by(desc(Metasmecanico.id)).first()
        return render_template(
            "/umDado.html",
            ultimo_dado=ultimo_dado,
            perfils=MetaMecanicos,
            perfil="MetaMecanico",
            produto="Valor Metas Mecânico",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addMetaMecanico", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addMetaMecanico():
    try:
        if request.method == "POST":
            meta = request.form.get("meta").strip()
            bonos = request.form.get("bonos").strip()
            filtro = Metasmecanico.query.order_by(desc(Metasmecanico.id)).first()
            if filtro.meta == meta:
                flash(
                    f"Esse ja é o Valor Atual da Meta!!!",
                    "cor-alerta",
                )
            elif meta == 0.00:
                flash(
                    f"O Valor R$ 0,00, Não é Valido!!!",
                    "cor-alerta",
                )
            elif Calculos_gloabal.valor_para_Calculos(
                meta
            ) > Calculos_gloabal.valor_para_Calculos(bonos):
                flash(
                    f"O Valor de Bonos não pode ser menor que a Meta!!!",
                    "cor-alerta",
                )
            else:
                valores = Metasmecanico(meta=meta, bonos=bonos)
                db.session.add(valores)
                flash(
                    f"O Valor Foi Atualizado com Sucesso!!!",
                    "cor-ok",
                )
                db.session.commit()
                return redirect(url_for("MetaMecanico"))
        return render_template(
            "/addUmDado.html",
            dado="",
            perfil="MetaMecanico",
            produto="Valor Metas Mecânico",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/MetaVendedor")
@login_required
@nome_required
@verificacao_nivel(4)
def MetaVendedor():
    try:
        page = request.args.get("page", 1, type=int)
        MetaVendedors = Metasvendedor.query.order_by(Metasvendedor.id.desc()).paginate(
            page=page, per_page=10
        )
        ultimo_dado = Metasvendedor.query.order_by(desc(Metasvendedor.id)).first()
        return render_template(
            "/umDado.html",
            ultimo_dado=ultimo_dado,
            perfils=MetaVendedors,
            perfil="MetaVendedor",
            produto="Valor Metas Vendedor",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addMetaVendedor", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addMetaVendedor():
    try:
        if request.method == "POST":
            meta = request.form.get("meta").strip()
            bonos = request.form.get("bonos").strip()
            filtro = Metasvendedor.query.order_by(desc(Metasvendedor.id)).first()
            if filtro.meta == MetaVendedor:
                flash(
                    f"Esse ja é o Valor Atual da Meta!!!",
                    "cor-alerta",
                )
            elif meta == 0.00:
                flash(
                    f"O Valor R$ 0,00, Não é Valido!!!",
                    "cor-alerta",
                )
            elif Calculos_gloabal.valor_para_Calculos(
                meta
            ) > Calculos_gloabal.valor_para_Calculos(bonos):
                flash(
                    f"O Valor de Bonos não pode ser menor que a Meta!!!",
                    "cor-alerta",
                )
            else:
                valores = Metasvendedor(meta=meta, bonos=bonos)
                db.session.add(valores)
                flash(
                    f"O Valor Foi Atualizado com Sucesso!!!",
                    "cor-ok",
                )
                db.session.commit()
                return redirect(url_for("MetaVendedor"))
        return render_template(
            "/addUmDado.html",
            dado="",
            perfil="MetaVendedor",
            produto="Valor Metas Vendedor",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

# Lembretes Para todos do inicil
@app.route("/Lembretes")
@login_required
@nome_required
def Lembretes():
    try:
        page = request.args.get("page", 1, type=int)
        lembretes = Lembretestodos.query.order_by(
            Lembretestodos.data_inicil.desc()
        ).paginate(page=page, per_page=10)
        return render_template("Lembretes/lembretes.html", lembretes=lembretes)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addLembretes", methods=["GET", "POST"])
@login_required
@nome_required
def addLembretes():
    form = LembretesMensagens()
    if request.method == "POST":
        gettitulo = request.form.get("titulo").strip()
        getmsg = request.form.get("msg").strip()
        getautor = request.form.get("autor").strip()
        gettipo = request.form.get("tipo")
        getdestinatario = request.form.get("destinatario")
        getdata_inicil = request.form.get("data_inicial")
        getdata_fim = request.form.get("data_fim")
        data_inicil_for = datetime.strptime(getdata_inicil, "%Y-%m-%d")
        data_fim_for = datetime.strptime(getdata_fim, "%Y-%m-%d")
        lembrete = Lembretestodos(
            titulo=gettitulo,
            msg=getmsg,
            tipo=gettipo,
            autor=getautor,
            destinatario=getdestinatario,
            data_inicil=data_inicil_for,
            data_fim=data_fim_for,
        )
        db.session.add(lembrete)
        db.session.commit()
        flash(
            f"O lembrete Foi Criado com Sucesso!!!",
            "cor-ok",
        )
        return redirect(url_for("Lembretes"))
    data_atual = datetime.now().date()
    data_final = data_atual + timedelta(days=30)
    data_formatada_inicil = data_atual.strftime("%Y-%m-%d")
    data_formatada_fim = data_final.strftime("%Y-%m-%d")
    return render_template("Lembretes/addLembrete.html",
                            form=form,
                            data_formatada_inicil=data_formatada_inicil,
                            data_formatada_fim=data_formatada_fim,)


@app.route("/atulizLembretes/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
def atulizLembretes(id):
    lembrete = Lembretestodos.query.get_or_404(id)
    if request.method == "POST":
        gettitulo = request.form.get("titulo").strip()
        getmsg = request.form.get("msg").strip()
        getautor = request.form.get("autor").strip()
        getdestinatario = request.form.get("destinatario").strip()
        gettipo = request.form.get("tipo")
        getdata_fim = request.form.get("data_fim").strip()
        getdata_inicil = request.form.get("data_inicial")
        getdata_fim = request.form.get("data_fim")
        data_inicial_for = datetime.strptime(getdata_inicil, "%Y-%m-%d")
        data_fim_for = datetime.strptime(getdata_fim, "%Y-%m-%d")

        lembrete.titulo = gettitulo
        lembrete.autor = getautor
        lembrete.destinatario = getdestinatario
        lembrete.tipo = gettipo
        lembrete.msg = getmsg
        lembrete.data_inicial = data_inicial_for
        lembrete.data_fim = data_fim_for
        db.session.commit()
        flash(
            f"O lembrete foi Atulizado com Sucesso!!!",
            "cor-ok",
        )
        return redirect("/Lembretes")
    form = LembretesMensagens(request.form)
    form.titulo.data = lembrete.titulo
    form.tipo.data = lembrete.tipo
    form.msg.data = lembrete.msg
    data_formatada = datetime.strptime(lembrete.data_inicil, "%Y-%m-%d %H:%M:%S")
    data_formatada_inicil = data_formatada.strftime("%Y-%m-%d")
    data_formatada = datetime.strptime(lembrete.data_fim, "%Y-%m-%d %H:%M:%S")
    data_formatada_fim = data_formatada.strftime("%Y-%m-%d")
    form.destinatario.data = lembrete.destinatario
    return render_template(
        "/Lembretes/addLembrete.html",
        lembrete=lembrete,
        form=form,
        data_formatada_inicil=data_formatada_inicil,
        data_formatada_fim=data_formatada_fim,
    )


@app.route("/deleteLembrete/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
def deleteLembrete(id):
    try:
        lembrete = Lembretestodos.query.get_or_404(id)
        if request.method == "POST":
            lembretedata_inicil = lembrete.data_inicil
            try:
                db.session.delete(lembrete)
                db.session.commit()
                flash(
                    f"O lembrete do data_inicil {lembretedata_inicil} foi Deletada",
                    "cor-ok",
                )
                return jsonify()
            except:
                flash(
                    f"O lembrete Não pode ser APAGADO, Ao invés de apagar modifique pois a Veiculos cadastrados com esse data_inicil!",
                    "cor-alerta",
                )
                return jsonify()
        flash(
            f"O lembrete com o data_inicil {lembretedata_inicil} NÂO foi Deletada",
            "cor-alerta",
        )
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

#Seviços

@login_required
@nome_required
@verificacao_nivel(2)
@app.route("/servicoRelatorios")
def servicoRelatorios():
    user = current_user
    page = request.args.get("page", 1, type=int)
    servisos = Serviso.query.filter(
        and_(
            Serviso.status == "Finalizado",
            Serviso.id != 0,
            or_(
                Serviso.vendedor_id == user.id,
                Serviso.mecanico_id == user.id
            )
        )
    ).order_by(Serviso.data_finalizada.desc()).paginate(page=page, per_page=10)
    return render_template(
        "Servicos/Servicos.html",
        status="meus servico",
        servisos=servisos,
    )


@app.route("/searchservicoRelatorios", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchservicoRelatorios():
    try:
       if request.method == "POST":
            user = current_user
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "placa":
                servisos = (
                    Serviso.query.join(Veiculo)
                    .filter(Veiculo.placa.like(search))
                    .filter(Serviso.status == "Finalizado",
                            or_(
                            Serviso.vendedor_id == user.id,
                            Serviso.mecanico_id == user.id
                        ))
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
            elif escolha == "modelo":
               servisos = (
                    Serviso.query.join(Veiculo).join(Carro)
                    .filter(Carro.modelo.like(search))
                    .filter(Serviso.status == "Finalizado",
                            or_(
                            Serviso.vendedor_id == user.id,
                            Serviso.mecanico_id == user.id
                        ))
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
            elif escolha == "datafor":
                try:
                    if len(busca) == 10:
                        data_hora_especifica = datetime(
                            int(busca[6:10:]),
                            int(busca[3:5:]),
                            int(busca[:2:]),
                            0,
                            0,
                            0,
                        )
                        query = Serviso.query.filter(
                            Serviso.data_finalizada > data_hora_especifica,
                            Serviso.status == "Finalizado",
                            or_(
                                Serviso.vendedor_id == user.id,
                                Serviso.mecanico_id == user.id
                            )
                        ).order_by(Serviso.data_finalizada.desc())

                        servisos = query.paginate(page=page, per_page=10)
                    elif len(busca) == 23:
                        data_inicial = datetime(
                            int(busca[6:10:]),
                            int(busca[3:5:]),
                            int(busca[:2:]),
                            0,
                            0,
                            0,
                        )
                        data_final = datetime(
                            int(busca[19:23:]),
                            int(busca[16:18:]),
                            int(busca[13:15:]),
                            0,
                            0,
                            0,
                        )
                        query = Serviso.query.filter(
                            Serviso.data_finalizada.between(data_inicial, data_final),
                            Serviso.status == "Finalizado",
                            or_(
                                Serviso.vendedor_id == user.id,
                                Serviso.mecanico_id == user.id
                            )
                        ).order_by(Serviso.data_finalizada.desc())
                        servisos = query.paginate(page=page, per_page=10)
                    else:
                        flash(
                            "Algo deu errado!!!! Confira a data digitada", "cor-alerta"
                        )
                        return redirect(url_for("servicoDoCliente", id=id))
                except:
                    flash("Algo deu errado!!!! Confira a data digitada", "cor-alerta")
                    return redirect(url_for("servicoDoCliente", id=id))
            else:
                servisos = (
                    Serviso.query.filter(getattr(Serviso, escolha).like(search))
                    .filter(Serviso.status == "Finalizado",
                            or_(
                                Serviso.vendedor_id == user.id,
                                Serviso.mecanico_id == user.id
                            ))
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
            return render_template(
                "Servicos/Servicos.html",
                status="meus servico",
                cliente_id =user,
                servisos=servisos,
                busca=busca,
                escolha=escolha,
            )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
    

@app.route("/carDinamicosUsuario/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def carDinamicosUsuario(id):
    users = User.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    servisos = Serviso.query.filter(
        and_(
            Serviso.status == "Finalizado",
            Serviso.id != 0,
            or_(
                Serviso.vendedor_id == users.id,
                Serviso.mecanico_id == users.id
            )
        )

    ).order_by(Serviso.data_finalizada.desc()).paginate(page=page, per_page=10)
    ganhos_por_mes = Serviso.query.with_entities(func.extract('month', Serviso.data_finalizada).label('mes'),
                                                 func.extract('year', Serviso.data_finalizada).label('ano'),
                                                 func.sum(func.replace(func.replace(func.replace(func.replace(Serviso.valor_ganho, 'R$', ''),'\xa0', ''), '.', ''), ',', '.').cast(Numeric)).label('ganhos_total')) \
                                    .filter(
                                        and_(
                                            Serviso.status == "Finalizado",
                                            Serviso.id != 0,
                                            or_(
                                                Serviso.vendedor_id == users.id,
                                                Serviso.mecanico_id == users.id
                                            )
                                        )
                                    ) \
                                    .group_by(func.extract('month', Serviso.data_finalizada), func.extract('year', Serviso.data_finalizada)) \
                                    .order_by(func.extract('year', Serviso.data_finalizada).desc(), func.extract('month', Serviso.data_finalizada).desc()) \
                                    .all()
    dados_formatados = []
    meses_em_portugues = {
        1: 'janeiro',2: 'fevereiro',3: 'março',4: 'abril',5: 'maio',6: 'junho',
        7: 'julho',8: 'agosto',9: 'setembro',10: 'outubro',11: 'novembro',12: 'dezembro'
    }
    for ganho in ganhos_por_mes:
        mes_nome = meses_em_portugues[ganho.mes]
        formatado_valor = Calculos_gloabal.format_valor_moeda(ganho.ganhos_total)
        if users.cargo_id == 3:
            meta_do_mes = Metasmecanico.query.filter(
                extract('year', Metasmecanico.dataModific) == ganho.ano,
                extract('month', Metasmecanico.dataModific) == ganho.mes
            ).order_by(Metasmecanico.dataModific).first()
            if not meta_do_mes:
                meta_do_mes = Metasmecanico.query.filter(
                    extract('year', Metasmecanico.dataModific) <= ganho.ano,
                    extract('month', Metasmecanico.dataModific) <= ganho.mes
                ).order_by(Metasmecanico.dataModific).first()
                if not meta_do_mes:
                    meta_do_mes = Metasmecanico.query.filter(
                        extract('year', Metasmecanico.dataModific) <= ganho.ano,
                        extract('month', Metasmecanico.dataModific) >= ganho.mes
                    ).order_by(Metasmecanico.dataModific).first()
                    if not meta_do_mes:
                        meta_do_mes = Metasmecanico.query.filter(
                            extract('year', Metasmecanico.dataModific) >= ganho.ano,
                            extract('month', Metasmecanico.dataModific) <= ganho.mes
                        ).order_by(Metasmecanico.dataModific).first()
                        if not meta_do_mes:
                            meta_do_mes = Metasmecanico.query.filter(
                                extract('year', Metasmecanico.dataModific) >= ganho.ano,
                                extract('month', Metasmecanico.dataModific) >= ganho.mes
                            ).order_by(Metasmecanico.dataModific).first()
                
        if users.cargo_id == 2:
            meta_do_mes = Metasvendedor.query.filter(
                extract('year', Metasvendedor.dataModific) == ganho.ano,
                extract('month', Metasvendedor.dataModific) == ganho.mes
            ).order_by(Metasvendedor.dataModific).first()
            if not meta_do_mes:
                meta_do_mes = Metasvendedor.query.filter(
                    extract('year', Metasvendedor.dataModific) <= ganho.ano,
                    extract('month', Metasvendedor.dataModific) <= ganho.mes
                ).order_by(Metasvendedor.dataModific).first()
                if not meta_do_mes:
                    meta_do_mes = Metasvendedor.query.filter(
                        extract('year', Metasvendedor.dataModific) <= ganho.ano,
                        extract('month', Metasvendedor.dataModific) >= ganho.mes
                    ).order_by(Metasvendedor.dataModific).first()
                    if not meta_do_mes:
                        meta_do_mes = Metasvendedor.query.filter(
                            extract('year', Metasvendedor.dataModific) >= ganho.ano,
                            extract('month', Metasvendedor.dataModific) <= ganho.mes
                        ).order_by(Metasvendedor.dataModific).first()
                        if not meta_do_mes:
                            meta_do_mes = Metasvendedor.query.filter(
                                extract('year', Metasvendedor.dataModific) >= ganho.ano,
                                extract('month', Metasvendedor.dataModific) >= ganho.mes
                            ).order_by(Metasvendedor.dataModific).first()
        ganho_formatado = {
            'mes': mes_nome,
            'ano': ganho.ano,
            'ganhos_total': formatado_valor,
            'meta': meta_do_mes.meta,
            'bonos': meta_do_mes.bonos,
            'batido': meta_do_mes.bonos,
            
        }
        dados_formatados.append(ganho_formatado)
    
    return render_template(
        "/Colaborador/vendasUsuario.html",
        status="meus servico",
        servisos=servisos,
        ganhos_por_mes=dados_formatados,
    )

