from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    request,
    jsonify,
)
from Site import db, app, nome_required, verificacao_nivel
from .modelos import Serviso
from Site.Global.fun_global import Calculos_gloabal, Redutor_codigo
from Site.Fornecedor.modelos import Fornecedor
from Site.Peças.modelos import Marcapeça, Peça
from Site.MaoObra.modelos import Maoobra, Catmaoobra, Nomemaoobra
from Site.Clientes.modelos import Cliente, Veiculo
from Site.Carros.modelos import Carro
from sqlalchemy import desc, and_, or_
import json
from datetime import datetime, timezone, timedelta
from Site.Caixa.modelos import Carteirabanco, Caixa
from flask_login import login_required
from Site.Admin.modelos import User
from .formularios import Responsaveis
from flask_login import login_required, current_user
import random



@app.route("/lop_criar_orcamentos")
@login_required
@nome_required
@verificacao_nivel(4)
def lop_criar_orcamentos():
    carros = Veiculo.query.all()
    for veiculo in carros:
        user = current_user
        num_items = Serviso.query.count()

        if num_items == 0:
            Redutor_codigo.Redutor_codigo_seriviços(veiculo.cliente_id, veiculo.id, user.id)
        else:
            filtro = Serviso.query.order_by(desc(Serviso.id)).first()
            get_serviso = Serviso.query.get_or_404(filtro.id)
            Cliente_os_atual = json.loads(get_serviso.cliente_veiculo)

            if len(Cliente_os_atual["itens"]) == 0 and get_serviso.cliente_os_id == 0:
                get_serviso.cliente_os_id = veiculo.cliente_id
                get_serviso.veiculo_os_id = veiculo.id
                get_serviso.user_os_id = user.id
                get_serviso.data_finalizada = datetime.now(timezone.utc).astimezone()
                db.session.commit()
            else:
                Redutor_codigo.Redutor_codigo_seriviços(veiculo.cliente_id, veiculo.id, user.id)
    return redirect("/")


@app.route("/lop_finalizar_todos_Serviço")
@login_required
@nome_required
@verificacao_nivel(4)
def lop_finalizar_todos_Serviço():
    servisoFinalizado = Serviso.query.all()
    lista_carteiras = []
    carteiras = Carteirabanco.query.filter().all()
    for carte in carteiras:
        lista_carteiras.append(carte.id)
    lista_mecanico = []
    lista_venda = []
    mecanicos = User.query.filter(or_(User.cargo_id == 3, User.cargo_id == 1)).all()
    for mecanico in mecanicos:
        lista_mecanico.append(mecanico.id)
    vendedors = User.query.filter(User.cargo_id <= 2).all()
    for vendedor in vendedors:
        lista_venda.append(vendedor.id)
    for serviç in servisoFinalizado:
        if serviç.status == "Finalizado":
            pass
        else:
            mais_menos = random.choice(['-', '+'])
            
            valor_pago_int = random.randint(1, 1000)
            valor_venda_int = valor_pago_int * 2
            valor_peças_int = valor_venda_int - random.randint(0, valor_pago_int)
            por_cento = valor_venda_int * (10 / 100.0) 
            if mais_menos == '+':
                valor_total_int = valor_venda_int + random.randint(0, int(por_cento))
            else:
                valor_total_int = valor_venda_int - random.randint(0, int(por_cento))

            km = random.randint(0, 100000)
            valor_gasto = float(valor_pago_int)
            valor_pesas = float(valor_peças_int)
            valor_total = float(valor_venda_int)
            valor_recebido = float(valor_total_int)
            
            valor_mdo = (valor_total) - (valor_pesas)
            if valor_mdo < 0:
                valor_mdo = 0
            valor_mdo = Calculos_gloabal.format_valor_moeda(valor_mdo)

            desconto_sobra =  valor_recebido - valor_total

            soma_ganho = valor_recebido - valor_gasto
            soma_ganho_form = Calculos_gloabal.format_valor_moeda(soma_ganho)
            valor_pesas_soma = (valor_pesas) - (valor_gasto) + (desconto_sobra)
            if valor_pesas_soma < 0:
                valor_mdo = soma_ganho_form
                valor_pesas_soma = 0
            valor_pesas_soma_forma = Calculos_gloabal.format_valor_moeda(valor_pesas_soma)

            carteira=random.choice(lista_carteiras)

            desconto_sobra = Calculos_gloabal.format_valor_moeda(desconto_sobra)
            valor_recebido = Calculos_gloabal.format_valor_moeda(valor_recebido)
            valor_total = Calculos_gloabal.format_valor_moeda(valor_total)
            valor_gasto = Calculos_gloabal.format_valor_moeda(valor_gasto)


            serviç.vendedor_id = random.choice(lista_venda)
            serviç.mecanico_id = random.choice(lista_mecanico)
            serviç.km_final = km
            carteira_valores = json.loads(serviç.carteira_id)
            novo_item = {
                "carteira_id": carteira,
                "valor_recebido": valor_total,
                "detalesPago": 'Valor Variavel',
                }
            carteira_valores["itens"].append(novo_item)
            serviç.carteira_id = json.dumps(carteira_valores)
            serviç.valor_pesas = valor_pesas_soma_forma
            serviç.valor_mdo = valor_mdo
            serviç.valor_gasto = valor_gasto
            serviç.valor_recebido = valor_recebido
            serviç.valor_total = valor_total
            serviç.desconto_sobra = desconto_sobra
            serviç.valor_ganho = soma_ganho_form
            serviç.status = "Finalizado"

            data_finalizacao = datetime(
                random.randint(2020, 2023),
                random.randint(1, 12),  # Mês
                random.randint(1, 28),  # Dia (ajuste conforme necessário)
                random.randint(0, 23),  # Hora
                random.randint(0, 59),  # Minuto
                random.randint(0, 59),  # Segundo
                tzinfo=timezone.utc
            )
            serviç.data_criado = data_finalizacao
            serviç.data_finalizada = data_finalizacao
            db.session.commit()
        
            novo_caixa = Caixa(
                pagopor=serviç.id,
                descricao='Valor Variavel',
                valor=soma_ganho_form,
                tipo="Entrada",
                carteira_id=int(carteira),
                catcaixa_id=1,
                fornecedor_id=0,
                data_criado=data_finalizacao,
            )
            db.session.add(novo_caixa)
            db.session.commit()
    return redirect(f"/servisos/Todo")

# Dados do Serviços
@app.route("/servisos/<string:status>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def servisos(status):
    try:
        user = current_user
        page = request.args.get("page", 1, type=int)
        if (
            (user.nivel) != "PERITO"
            and user.nivel != "ESPECIALISTA"
            and user.nivel != "DONO"
            and user.nivel != "COMPETENTE"
        ):
            if status == "Todo":
                servisos = (
                    Serviso.query.filter(
                        (Serviso.id != 0)
                        & (Serviso.user_os_id == user.id)
                        & (
                            (Serviso.cliente_veiculo != '{"itens": []}')
                            | (Serviso.cliente_os_id != 0)
                        )
                    )
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                servisos = (
                    Serviso.query.filter(
                        (Serviso.status == status)
                        & (Serviso.id != 0)
                        & (Serviso.user_os_id == user.id)
                        & (
                            (Serviso.cliente_veiculo != '{"itens": []}')
                            | (Serviso.cliente_os_id != 0)
                        )
                    )
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
        else:
            if status == "Todo":
                servisos = (
                    Serviso.query.filter(
                        (Serviso.id != 0)
                        & (
                            (Serviso.cliente_veiculo != '{"itens": []}')
                            | (Serviso.cliente_os_id != 0)
                        )
                    )
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                servisos = (
                    Serviso.query.filter(
                        (Serviso.status == status)
                        & (Serviso.id != 0)
                        & (
                            (Serviso.cliente_veiculo != '{"itens": []}')
                            | (Serviso.cliente_os_id != 0)
                        )
                    )
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
        return render_template(
            "Serviços/Serviços.html",
            status=status,
            servisos=servisos,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchServiso/<string:status>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def searchServiso(status):
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "nome":
                if status == "Todo":
                    get_servisos = (
                        Serviso.query.filter(
                            or_(
                                Serviso.cliente_os.has(Cliente.nome.like(search)),
                                Serviso.cliente_veiculo.like(f'%"{search}"%'),
                                Serviso.cliente_os.has(
                                    Cliente.nomeFantasia.like(search)
                                ),
                            )
                        )
                        .filter(Serviso.id != 0)
                        .order_by(Serviso.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    get_servisos = (
                        Serviso.query.filter(
                            or_(
                                Serviso.cliente_os.has(Cliente.nome.like(search)),
                                Serviso.cliente_veiculo.like(f'%"{search}"%'),
                                Serviso.cliente_os.has(
                                    Cliente.nomeFantasia.like(search)
                                ),
                            ),
                            Serviso.status == status,
                            Serviso.id != 0,
                        )
                        .order_by(desc(Serviso.data_criado))
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
                        if status == "Todo":
                            query = Serviso.query.filter(
                                Serviso.data_finalizada > data_hora_especifica,
                                Serviso.id != 0,
                            ).order_by(Serviso.data_finalizada.desc())
                        else:
                            query = Serviso.query.filter(
                                Serviso.data_finalizada > data_hora_especifica,
                                Serviso.status == status,
                                Serviso.id != 0,
                            ).order_by(Serviso.data_finalizada.desc())
                        get_servisos = query.paginate(page=page, per_page=10)
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
                        if status == "Todo":
                            query = Serviso.query.filter(
                                Serviso.data_finalizada.between(
                                    data_inicial, data_final
                                ),
                            ).order_by(Serviso.data_finalizada.desc())
                        else:
                            query = Serviso.query.filter(
                                Serviso.data_finalizada.between(
                                    data_inicial, data_final
                                ),
                                Serviso.status == status,
                            ).order_by(Serviso.data_finalizada.desc())
                        get_servisos = query.paginate(page=page, per_page=10)
                    else:
                        flash(
                            "Algo deu errado!!!! Confira a data digitada", "cor-alerta"
                        )
                        return redirect(url_for("servisos", status=status))
                except:
                    flash("Algo deu errado!!!! Confira a data digitada", "cor-alerta")
                    return redirect(url_for("servisos", status=status))
            elif escolha == "todos":
                search_terms = search.split()  
                conditions = []
                for term in search_terms:
                    conditions.append(
                        or_(
                            Serviso.id.like(f'%{term}%'),
                            Serviso.notafiscal.like(f'%{term}%'),
                            Serviso.status.like(f'%{term}%'),
                            Serviso.cliente_veiculo.like(f'%{term}%'),
                            Serviso.data_criado.like(f'%{term}%'),
                            Serviso.data_finalizada.like(f'%{term}%'),
                            Serviso.peça_os.like(f'%{term}%'),
                            Serviso.mo_os.like(f'%{term}%'),
                            Serviso.obs.like(f'%{term}%'),
                            Serviso.km_final.like(f'%{term}%'),
                            Serviso.carteira_id.like(f'%{term}%'),
                            Serviso.valor_pesas.like(f'%{term}%'),
                            Serviso.valor_mdo.like(f'%{term}%'),
                            Serviso.valor_gasto.like(f'%{term}%'),
                            Serviso.valor_recebido.like(f'%{term}%'),
                            Serviso.valor_total.like(f'%{term}%'),
                            Serviso.desconto_sobra.like(f'%{term}%'),
                            Serviso.valor_ganho.like(f'%{term}%'),

                            Serviso.cliente_os.has(Cliente.nome.like(f'%{term}%')), 
                            Serviso.cliente_os.has(Cliente.fone.like(f'%{term}%')), 

                            Serviso.veiculo_os.has(Veiculo.placa.like(f'%{term}%')),
                            Serviso.veiculo_os.has(Veiculo.carro.has(Carro.marca.like(f'%{term}%'))),
                            Serviso.veiculo_os.has(Veiculo.carro.has(Carro.modelo.like(f'%{term}%'))),
                            Serviso.veiculo_os.has(Veiculo.carro.has(Carro.ano.like(f'%{term}%'))),
                            Serviso.veiculo_os.has(Veiculo.carro.has(Carro.motor.like(f'%{term}%'))),

                            Serviso.user_os.has(User.nome.like(f'%{term}%')),
                            Serviso.mecanico.has(User.nome.like(f'%{term}%')),
                            Serviso.vendedor.has(User.nome.like(f'%{term}%')),
                            Serviso.vendedor.has(User.apelido.like(f'%{term}%')),
                            Serviso.vendedor.has(User.apelido.like(f'%{term}%')),
                            Serviso.vendedor.has(User.apelido.like(f'%{term}%')),
                        )
                    )
                get_servisos = (
                    Serviso.query.filter(
                        *conditions
                    )
                    .order_by(Serviso.id.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                if status == "Todo":
                    get_servisos = (
                        Serviso.query.filter(getattr(Serviso, escolha).like(search))
                        .filter(Serviso.id != 0)
                        .order_by(Serviso.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    get_servisos = (
                        Serviso.query.filter(getattr(Serviso, escolha).like(search))
                        .filter(Serviso.status == status)
                        .filter(Serviso.id != 0)
                        .order_by(Serviso.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
            return render_template(
                "Serviços/Serviços.html",
                status=status,
                servisos=get_servisos,
                busca=busca,
                escolha=escolha,
            )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deleteServisos/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteServisos(id):
    try:
        servisos = Serviso.query.get_or_404(id)
        if request.method == "POST":
            servisosnome = servisos.id
            try:
                data_hora_atual = datetime.now()
                ano_atual = int(data_hora_atual.year)
                mes_atual = int(data_hora_atual.month)
                data_hora_especifica = datetime(
                    ano_atual,
                    mes_atual,
                    1,
                    0,
                    0,
                    0,
                )
                filtro = servisos.query.filter(
                    and_(
                        servisos.data_finalizada > data_hora_especifica,
                        servisos.status == "Finalizado",
                    )
                ).first()
                filtro2 = servisos.query.filter(
                    servisos.status != "Finalizado",
                ).first()
                if filtro:
                    getCaixa = Caixa.query.filter(
                        and_(
                            Caixa.pagopor == servisos.id,
                            Caixa.catcaixa_id == "1",
                        )
                    ).all()
                    if getCaixa:
                        for apagar  in getCaixa:
                            db.session.delete(apagar)
                    db.session.commit()
                    db.session.delete(servisos)
                    db.session.commit()
                    flash(
                        f"O Serviço com ID: {servisosnome} foi Deletada com Sucesso!!!",
                        "cor-ok",
                    )
                    return jsonify()
                elif filtro2:
                    if servisos.status == "Aprovado":
                        peças_os = json.loads(servisos.peça_os)
                        getPeça = Peça.query.order_by(Peça.id)
                        for peça_um in getPeça:
                            for item in peças_os["itens"]:
                                peçaid = item.get("peça_id")
                                peçaParaEstoque = item.get("em_estoque")
                                if peçaid == peça_um.id:
                                    peça_modificar = Peça.query.get_or_404(peça_um.id)
                                    if int(peçaParaEstoque) != 0:
                                        valor_atual = int(peçaParaEstoque) + int(
                                            peça_modificar.estoque
                                        )
                                        peça_modificar.estoque = valor_atual
                                        db.session.commit()
                    db.session.delete(servisos)
                    db.session.commit()
                    flash(
                        f"O Serviço com ID: {servisosnome} foi Deletada com Sucesso!!!",
                        "cor-ok",
                    )
                    return jsonify()
                else:
                    flash(
                        f"O Serviço com ID: {servisosnome} não foi APAGADA, O Seviços dos meses anteriores não podem ser apagados!",
                        "cor-cancelar",
                    )
                return jsonify()
            except Exception as erro:
                flash(
                    f"{erro} .O Serviço com ID: {servisosnome} NÃo pode ser APAGADO.",
                    "cor-alerta",
                )
                return jsonify()
        flash(f"O servisos {servisosnome} NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/AddServiço", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def AddServiço():
    num_items = Serviso.query.count()
    if num_items == 0:
        Redutor_codigo.Redutor_codigo_seriviços(0, 0, 0)
    filtro = Serviso.query.order_by(desc(Serviso.id)).first()
    get_serviso = Serviso.query.get_or_404(filtro.id)
    Cliente_os_atual = json.loads(get_serviso.cliente_veiculo)
    if len(Cliente_os_atual["itens"]) > 0 or get_serviso.cliente_os_id > 0:
        Redutor_codigo.Redutor_codigo_seriviços(0, 0, 0)
    filtro = Serviso.query.order_by(desc(Serviso.id)).first()
    Serviço = filtro
    return redirect(f"/AbrirServiço/{Serviço.id}/tratatar")


@app.route("/AbrirServiço/<int:id>/<string:tratatar>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def AbrirServiço(id, tratatar):
    form = Responsaveis()
    get_serviso = Serviso.query.get_or_404(id)
    if tratatar == "alertar" and get_serviso.status != "Finalizado":
        flash(
            "Os dados modificados aqui serão automaticamente atualizados.",
            "cor-alerta",
        )
    if not get_serviso:
        return "Serviço não encontrado", 404

    peça_os = json.loads(get_serviso.peça_os)
    getPeças = Peça.query.order_by(Peça.id).all()
    mo_os = json.loads(get_serviso.mo_os)
    get_MDO = Maoobra.query.order_by(Maoobra.id).all()
    carteira_serviço = json.loads(get_serviso.carteira_id)
    carteiras = Carteirabanco.query.filter().all()
    Cliente_os_atual = json.loads(get_serviso.cliente_veiculo)
    nome_cliente_os, nome_telefone_os, nome_email_os = "", "", ""
    placa, marca, modelo, ano, motor, km = "", "", "", "", "", ""

    if len(Cliente_os_atual["itens"]) > 0:
        for item in Cliente_os_atual["itens"]:
            nome_cliente_os = item.get("nome")
            nome_telefone_os = item.get("telefone")
            nome_email_os = item.get("email")
            placa = item.get("placa")
            marca = item.get("marca")
            modelo = item.get("modelo")
            ano = item.get("ano")
            motor = item.get("motor")
            km = item.get("km")

    items_data_peças = []
    soma_pagos = []
    soma_peças = []
    soma_total = []
    if "itens" in peça_os:
        for item in peça_os["itens"]:
            peça_id = item.get("peça_id")
            un = item.get("un")
            peça_nome = item.get("peça_nome")
            lado = item.get("lado")
            valor_final = item.get("valor_final")
            peça_codigo = item.get("peça_codigo")
            valor_custo = item.get("valor_custo")
            if peça_id is not None:
                if len(getPeças) == 0 :
                    Pagosoma = Calculos_gloabal.valor_para_Calculos(
                        valor_custo
                    ) * int(un)
                    PagoFor = Calculos_gloabal.format_valor_moeda(Pagosoma)
                    soma_pagos.append(Pagosoma)
                    somar_dados_uni = Calculos_gloabal.valor_para_Calculos(valor_final)
                    soma_do_valor = int(un) * somar_dados_uni
                    soma_peças.append(soma_do_valor)
                    soma_total.append(soma_do_valor)
                    soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                    items_data_peças.append(
                                {
                                    "codigo": peça_codigo,
                                    "nome": peça_nome,
                                    "preso": valor_final,
                                    "pago_total": soma_formarmatado,
                                    "pago": PagoFor,
                                    "un": un,
                                    "lado": lado,
                                }
                            )
                for getPeça in getPeças:
                    Pagosoma = Calculos_gloabal.valor_para_Calculos(
                        getPeça.pago
                    ) * int(un)
                    PagoFor = Calculos_gloabal.format_valor_moeda(Pagosoma)
                    soma_pagos.append(Pagosoma)
                    if getPeça.id == peça_id:
                        if get_serviso.status != "Orçamento":
                            somar_dados_uni = Calculos_gloabal.valor_para_Calculos(valor_final)
                            soma_do_valor = int(un) * somar_dados_uni
                            soma_peças.append(soma_do_valor)
                            soma_total.append(soma_do_valor)
                            soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                            items_data_peças.append(
                                    {
                                        "codigo": peça_codigo,
                                        "nome": peça_nome,
                                        "preso": valor_final,
                                        "pago_total": soma_formarmatado,
                                        "pago": PagoFor,
                                        "un": un,
                                        "lado": lado,
                                    }
                                )
                        else:
                            somar_dados_uni = Calculos_gloabal.valor_para_Calculos(getPeça.preso)
                            soma_do_valor = int(un) * somar_dados_uni
                            soma_peças.append(soma_do_valor)
                            soma_total.append(soma_do_valor)
                            soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                            items_data_peças.append(
                                {
                                    "codigo": getPeça.codigo,
                                    "nome": getPeça.nome,
                                    "preso": getPeça.preso,
                                    "pago_total": soma_formarmatado,
                                    "pago": PagoFor,
                                    "un": un,
                                    "lado": lado,
                                }
                            )
                    else:
                        Pagosoma = Calculos_gloabal.valor_para_Calculos(
                            valor_custo
                        ) * int(un)
                        PagoFor = Calculos_gloabal.format_valor_moeda(Pagosoma)
                        somar_dados_uni = Calculos_gloabal.valor_para_Calculos(valor_final)
                        soma_do_valor = int(un) * somar_dados_uni
                        soma_peças.append(soma_do_valor)
                        soma_total.append(soma_do_valor)
                        soma_formarmatado = Calculos_gloabal.format_valor_moeda(soma_do_valor)
                        items_data_peças.append(
                                    {
                                        "codigo": peça_codigo,
                                        "nome": peça_nome,
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
                for getmo in get_MDO:
                    if getmo.id == mo_id:
                        if get_serviso.status != "Orçamento":
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
                    else:
                        mdo_valor_para_soma = Calculos_gloabal.valor_para_Calculos(mo_preso)
                        soma_total.append(mdo_valor_para_soma)
                        items_data_MDO.append(
                            {
                                "nome": mo_nome,
                                "preso": mo_preso,
                            }
                        )
    SomarPago = sum(soma_pagos)
    SomarPeças = sum(soma_peças)
    SomarTotal = sum(soma_total)

    valor_total_pago = Calculos_gloabal.format_valor_moeda(SomarPago)
    valor_total_peças = Calculos_gloabal.format_valor_moeda(SomarPeças)
    valor_total_total = Calculos_gloabal.format_valor_moeda(SomarTotal)

    status = get_serviso.status
    if tratatar == "Editar":
        status = "Editar Finazados"

    mecanicos = User.query.filter(or_(User.cargo_id == 3, User.cargo_id == 1)).all()
    if get_serviso.mecanico_id == 0:
        mecanico_choices = [("0", "Selecione Mecanico")] + [
            (mecanico.id, mecanico.apelido) for mecanico in mecanicos
        ]
    else:
        mecanico_choices = (
            [(get_serviso.mecanico.id, get_serviso.mecanico.apelido)]
            + [("0", "Selecione Mecanico")]
            + [(mecanico.id, mecanico.apelido) for mecanico in mecanicos]
        )
    form.mecanico.choices = mecanico_choices
    vendedors = User.query.filter(User.cargo_id <= 2).all()
    if get_serviso.vendedor_id == 0:
        vendedor_choices = [("0", "Selecione Vendedor")] + [
            (vendedor.id, vendedor.apelido) for vendedor in vendedors
        ]
    else:
        vendedor_choices = (
            [(get_serviso.vendedor.id, get_serviso.vendedor.apelido)]
            + [("0", "Selecione Vendedor")]
            + [(vendedor.id, vendedor.apelido) for vendedor in vendedors]
        )
    form.vendedor.choices = vendedor_choices
    
    items_data_carteira = []
    if "itens" in carteira_serviço:
        for item_carteira in carteira_serviço["itens"]:
            carteira_id_serviço = item_carteira.get("carteira_id")
            carteira_preso_serviço = item_carteira.get("valor_recebido")
            carteira_detales_serviço = item_carteira.get("detalesPago")
            if carteira_id_serviço is not None:
                for getcarteira in carteiras:
                    if int(getcarteira.id) == int(carteira_id_serviço):
                        items_data_carteira.append(
                            {
                                "carteira_id":carteira_id_serviço,
                                "carteira_nome":getcarteira.nome,
                                "valor_recebido":carteira_preso_serviço,
                                "detalesPago":carteira_detales_serviço,
                            }
                        )
    return render_template(
        "/Serviços/addServiços.html",
        Serviço=get_serviso,
        status=status,
        items_data_peças=items_data_peças,
        items_data_MDO=items_data_MDO,
        nome_cliente_os=nome_cliente_os,
        nome_telefone_os=nome_telefone_os,
        nome_email_os=nome_email_os,
        placa=placa,
        marca=marca,
        modelo=modelo,
        ano=ano,
        motor=motor,
        km=km,
        valor_total_pago=valor_total_pago,
        form=form,
        carteiras=carteiras,
        items_data_carteira=items_data_carteira,
        valor_total_peças=valor_total_peças,
        valor_total_total=valor_total_total,
    )


# Peças do Serviços
@app.route("/AddItensManual/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def AddItensManual(id):
    get_serviso = Serviso.query.get_or_404(id)
    try:
        if request.method == "POST":
            tipo = request.form.get("tipo")
            codigo = request.form.get("Codigo").upper()
            NomeItens = request.form.get("NomeItens").upper()
            unidad = request.form.get("unidad")
            lado = request.form.get("lado")
            custo = request.form.get("custo")
            venda = request.form.get("venda")
            codigo = '*' +  codigo
            if tipo == 'Peça':
                peça_os_atual = json.loads(get_serviso.peça_os)
                novo_item = {
                    "peça_id": 0,
                    "peça_codigo": codigo,
                    "peça_nome": NomeItens,
                    "un": unidad,
                    "lado": lado,
                    "em_estoque": 0,
                    "valor_custo": custo,
                    "valor_final": venda,
                }
                peça_os_atual["itens"].append(novo_item)
                get_serviso.peça_os = json.dumps(peça_os_atual)
            else: 
                MaoObra_os_atual = json.loads(get_serviso.mo_os)
                novo_item = {
                    "MDO_id": 0,
                    "MDO_nome": NomeItens,
                    "MDO_preso": venda,
                }
                MaoObra_os_atual["itens"].append(novo_item)
                get_serviso.mo_os = json.dumps(MaoObra_os_atual)
            db.session.commit()
            if get_serviso.id == 0:
                return redirect(f"/AbrirServiço/0/Editar")
            else:
                return redirect(f"/AbrirServiço/{get_serviso.id}/tratatar")
        flash(f"{get_serviso.id}", "itensServiço")
        if get_serviso.id == 0:
                return redirect(f"/AbrirServiço/0/Editar")
        else:
            return redirect(f"/AbrirServiço/{get_serviso.id}/tratatar")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

@app.route("/EscolhaPeças/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def EscolhaPeças(id):
    try:
        get_serviso = Serviso.query.get_or_404(id)
        page = request.args.get("page", 1, type=int)
        getPeça = Peça.query.order_by(Peça.id.desc()).paginate(page=page, per_page=10)
        CatPeça = Marcapeça.query.all()
        fornecedors = Fornecedor.query.all()
        return render_template(
            "/Peças/Peça.html",
            Adicionar=get_serviso,
            Peças=getPeça,
            marcas=CatPeça,
            fornecedors=fornecedors,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route(
    "/adicinar_item_peça", methods=["PUT"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def adicinar_item_peça():
    id_serviço = request.form.get("numero_servico")
    id_peça = request.form.get("numero_peca")
    get_serviso = Serviso.query.get_or_404(id_serviço)
    if get_serviso.id != 0 and get_serviso.status == "Finalizado":
        return redirect(f"/AbrirServiço/{get_serviso.id}/tratatar")
    else:
        getPeça = Peça.query.get_or_404(id_peça)
        numero = request.form.get("unidad")
        lado = request.form.get("lado")
        peça_os_atual = json.loads(get_serviso.peça_os)
        if not Serviso:
            return "Serviço não encontrado", 404
        if len(peça_os_atual["itens"]) > 0:
            for item in peça_os_atual["itens"]:
                peçaid = item.get("peça_id")
                if peçaid == getPeça.id:
                    flash=f"A Peça com ID {getPeça.id} Já foi adicionado ao Orçamento!!!"
                    response_data = {
                        "success": True,
                        "message": flash,
                        "cor": "cor-alerta",
                    }
                    return jsonify(response_data)
        valor_estoque = 0
        if get_serviso.status == "Aprovado":
            if getPeça.estoque != 0:
                valor_atual = int(getPeça.estoque) - int(numero)
                if int(getPeça.estoque) > int(numero):
                    valor_estoque = numero
                else:
                    valor_estoque = getPeça.estoque
                if valor_atual < 0:
                    valor_atual = 0
                getPeça.estoque = valor_atual
                db.session.commit()
        novo_item = {
            "peça_id": getPeça.id,
            "peça_codigo": getPeça.codigo,
            "peça_nome": getPeça.nome,
            "un": numero,
            "lado": lado,
            "em_estoque": valor_estoque,
            "valor_custo": getPeça.pago,
            "valor_final": getPeça.preso,
        }
        peça_os_atual["itens"].append(novo_item)
        get_serviso.peça_os = json.dumps(peça_os_atual)

        db.session.commit()
        flash = f"A Peça foi Adicionada com Sucesso!!!"
        
        response_data = {
            "success": True,
            "message": flash,
            "cor": "cor-ok",
        }
    return jsonify(response_data)



@app.route("/atualizar_uni_peças/<int:servico_id>/<int:item_id>", methods=["PUT"])
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_uni_peças(servico_id, item_id):
    try:
        servico = Serviso.query.get(servico_id)
        quantity = int(request.form.get("un"))
        if not servico:
            flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
        if servico.id != 0 and servico.status == "Finalizado":
            pass
        else:
            peça_os_atual = json.loads(servico.peça_os)

            if item_id < 0 or item_id >= len(peça_os_atual.get("itens", [])):
                flash(
                    "Índice do item inválido. Consulte o Desenvolvedor!!!",
                    "cor-cancelar",
                )

            em_id = peça_os_atual["itens"][item_id]["peça_id"]
            em_estoque = peça_os_atual["itens"][item_id]["em_estoque"]
            em_uni = peça_os_atual["itens"][item_id]["un"]
            if servico.status == "Aprovado":
                getPeça = Peça.query.get(em_id)
                if getPeça:
                    if int(quantity) < int(em_uni):
                        if int(em_estoque) > 0 and int(em_estoque) >= int(em_uni):
                            valor_estoque = int(getPeça.estoque) + 1
                        else:
                            em_estoque = em_estoque
                            valor_estoque = getPeça.estoque
                        if int(em_estoque) >= int(em_uni):
                            em_estoque = int(em_estoque) - 1
                    elif int(quantity) > int(em_uni):
                        if int(getPeça.estoque) > 0:
                            em_estoque = int(em_estoque) + 1
                        else:
                            em_estoque = em_estoque
                            valor_estoque = getPeça.estoque
                        valor_estoque = int(getPeça.estoque) - 1
                    if em_estoque < 0:
                        em_estoque = 0
                    if valor_estoque < 0:
                        valor_estoque = 0
                    getPeça.estoque = valor_estoque
                    db.session.commit()
            peça_os_atual["itens"][item_id]["em_estoque"] = em_estoque
            peça_os_atual["itens"][item_id]["un"] = quantity
            servico.peça_os = json.dumps(peça_os_atual)
            db.session.commit()
        return jsonify({"message": "Item atualizado com sucesso"})
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atualizar_lado_peças/<int:servico_id>/<int:item_id>", methods=["PUT"])
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_lado_peças(servico_id, item_id):
    servico = Serviso.query.get(servico_id)
    lado = str(request.form.get("lado"))

    if not servico:
        flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
    if servico.id != 0 and servico.status == "Finalizado":
        pass
    else:
        peça_os_atual = json.loads(servico.peça_os)

        if item_id < 0 or item_id >= len(peça_os_atual.get("itens", [])):
            flash(
                "Índice do item inválido. Consulte o Desenvolvedor!!!", "cor-cancelar"
            )

        peça_os_atual["itens"][item_id]["lado"] = lado

        servico.peça_os = json.dumps(peça_os_atual)

        db.session.commit()

    return jsonify({"message": "Item atualizado com sucesso"})


@app.route(
    "/apagar_item_peças/<int:servico_id>/<int:item_index>", methods=["POST", "DELETE"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def apagar_item_peças(servico_id, item_index):
    try:
        servico = Serviso.query.get(servico_id)
        if not servico:
            flash(
                f"Algo deu Errado Consulte o Desenvovedor!!!",
                "cor-cancelar",
            )
        if servico.id != 0 and servico.status == "Finalizado":
            return redirect(f"/AbrirServiço/{servico.id}/tratatar")
        else:
            peça_os_atual = json.loads(servico.peça_os)
            em_id = int(peça_os_atual["itens"][item_index]["peça_id"])
            em_estoque = peça_os_atual["itens"][item_index]["em_estoque"]

            if item_index < 0 or item_index >= len(peça_os_atual.get("itens", [])):
                flash(
                    f"Algo deu Errado Consulte o Desenvovedor!!!",
                    "cor-cancelar",
                )
            if servico.status == "Aprovado":
                getPeça = Peça.query.get(em_id)
                if getPeça:
                    if getPeça.estoque != 0:
                        valor_atual = int(em_estoque) + int(getPeça.estoque)
                        getPeça.estoque = valor_atual
                        db.session.commit()

            peça_os_atual["itens"].pop(item_index)
            servico.peça_os = json.dumps(peça_os_atual)

            db.session.commit()
            if servico.status == "Editar":
                return redirect(f"/AbrirServiço/{servico.id}/Editar")
            else:
                return redirect(f"/AbrirServiço/{servico.id}/dados")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchPeçasAdicionar", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def searchPeçasAdicionar():
    try:
        if request.method == "POST":
            id = request.form.get("id")
            get_serviso = Serviso.query.get_or_404(id)
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "marca":
                get_Peças = Peça.query.filter(
                    Peça.marca.has(Marcapeça.nome.like(search))
                ).paginate(page=page, per_page=4)
            elif escolha == "fornecedor":
                get_Peças = Peça.query.filter(
                    Peça.fornecedor.has(Fornecedor.nome.like(search))
                ).paginate(page=page, per_page=4)
            else:
                get_Peças = (
                    Peça.query.filter(getattr(Peça, escolha).like(search))
                    .order_by(Peça.id.desc())
                    .paginate(page=page, per_page=10)
                )
            marcaPesa = Marcapeça.query.all()
            return render_template(
                "Peças/Peça.html",
                Adicionar=get_serviso,
                Peças=get_Peças,
                busca=busca,
                escolha=escolha,
                CatPeça=marcaPesa,
            )
        else:
            return redirect("EscolhaMDOs")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Mao de obra Para serviço
@app.route("/EscolhaMDO/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def EscolhaMDO(id):
    get_serviso = Serviso.query.get_or_404(id)
    if request.method == "POST":
        MDOId = request.form.get("id")
        getMDO = Maoobra.query.get_or_404(MDOId)

        MDO_os_atual = json.loads(get_serviso.mo_os)

        if not Serviso:
            return "Serviço não encontrado", 404

        novo_item = {
            "MDO_id": getMDO.id,
        }
        MDO_os_atual["itens"].append(novo_item)
        get_serviso.mo_os = json.dumps(MDO_os_atual)

        db.session.commit()
        flash(
            f"A Mão de Obra foi Adicionada com Sucesso!!!",
            "cor-ok",
        )
        return redirect(f"/EscolhaMDO/{get_serviso.id}")
    page = request.args.get("page", 1, type=int)
    MaoObras = Maoobra.query.order_by(Maoobra.id.desc()).paginate(
        page=page, per_page=10
    )
    CatMaoObra = Catmaoobra.query.all()
    NomeMaoObra = Nomemaoobra.query.all()
    return render_template(
        "MaoObras/maoObra.html",
        Adicionar=get_serviso,
        MaoObras=MaoObras,
        NomeMaoObra=NomeMaoObra,
        CatMaoObra=CatMaoObra,
    )


@app.route(
    "/adicinar_item_MaoObra", methods=["PUT"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def adicinar_item_MaoObra():
    id_serviço = request.form.get("numero_servico")
    id_mdo = request.form.get("numero_mdo")
    get_serviso = Serviso.query.get_or_404(id_serviço)
    getMaoObra = Maoobra.query.get_or_404(id_mdo)
    MaoObra_os_atual = json.loads(get_serviso.mo_os)

    if not Serviso:
        return "Serviço não encontrado", 404
    if get_serviso.id != 0 and get_serviso.status == "Finalizado":
        return redirect(f"/AbrirServiço/{get_serviso.id}/tratatar")
    else:
        if len(MaoObra_os_atual["itens"]) > 0:
            for item in MaoObra_os_atual["itens"]:
                mo_id = item.get("MDO_id")
                if mo_id == getMaoObra.id:
                    flash=f"A Mão de Obra com ID {getMaoObra.id} Já foi adicionado ao Orçamento!!!"
                    
                    response_data = {
                        "success": True,
                        "message": flash,
                        "cor": "cor-alerta",
                    }
                    return jsonify(response_data)
        novo_item = {
            "MDO_id": getMaoObra.id,
            "MDO_nome": getMaoObra.nomemaoobra.nome,
            "MDO_preso": getMaoObra.preso,
        }
        MaoObra_os_atual["itens"].append(novo_item)
        get_serviso.mo_os = json.dumps(MaoObra_os_atual)
        db.session.commit()
        flash="A Mão de Obra foi Adicionada com Sucesso!!!"
        response_data = {
                        "success": True,
                        "message": flash,
                        "cor": "cor-ok",
                    }
        return jsonify(response_data)

@app.route("/searchMDOAdicionar", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def searchMDOAdicionar():
    try:
        if request.method == "POST":
            id = request.form.get("id")
            get_serviso = Serviso.query.get_or_404(id)
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "nome":
                MaoObras = Maoobra.query.filter(
                    Maoobra.nomemaoobra.has(Nomemaoobra.nome.like(search))
                ).paginate(page=page, per_page=10)
            elif escolha == "categoria":
                MaoObras = Maoobra.query.filter(
                    Maoobra.catmaoobra.has(Catmaoobra.nome.like(search))
                ).paginate(page=page, per_page=10)
            else:
                MaoObras = (
                    Maoobra.query.filter(getattr(Maoobra, escolha).like(search))
                    .order_by(Maoobra.id.desc())
                    .paginate(page=page, per_page=10)
                )
            CatMaoObra = Catmaoobra.query.all()
            NomeMaoObra = Nomemaoobra.query.all()
            return render_template(
                "MaoObras/maoObra.html",
                Adicionar=get_serviso,
                MaoObras=MaoObras,
                busca=busca,
                escolha=escolha,
                NomeMaoObra=NomeMaoObra,
                CatMaoObra=CatMaoObra,
            )
        else:
            return redirect("/EscolhaMDO")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route(
    "/apagar_item_mos/<int:servico_id>/<int:item_index>", methods=["POST", "DELETE"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def apagar_item_mos(servico_id, item_index):
    try:
        servico = Serviso.query.get(servico_id)
        if not servico:
            flash(
                f"Algo deu Errado Consulte o Desenvovedor!!!",
                "cor-cancelar",
            )
        if servico.id != 0 and servico.status == "Finalizado":
            return redirect(f"/AbrirServiço/{servico.id}/tratatar")
        else:
            mo_os_atual = json.loads(servico.mo_os)
            if item_index < 0 or item_index >= len(mo_os_atual.get("itens", [])):
                flash(
                    f"Algo deu Errado Consulte o Desenvovedor!!!",
                    "cor-cancelar",
                )

            mo_os_atual["itens"].pop(item_index)
            servico.mo_os = json.dumps(mo_os_atual)
            db.session.commit()
            if servico.status == "Editar":
                return redirect(f"/AbrirServiço/{servico.id}/Editar")
            else:
                return redirect(f"/AbrirServiço/{servico.id}/dados")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Dados cliente Orçamento
@app.route(
    "/atualizar_cliente_os/<int:Ser_id>/<string:clientName>/<string:telefone>/<string:email>/<string:placa>/<string:marca>/<string:modelo>/<string:ano>/<string:motor>/<string:km>",
    methods=["PUT"],
)
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_cliente_os(
    Ser_id, clientName, telefone, email, placa, marca, modelo, ano, motor, km
):
    try:
        user = current_user
        CliNome = str(clientName).upper()
        servico = Serviso.query.get(Ser_id)
        if not servico:
            flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")

        cliente_os_atual = json.loads(servico.cliente_veiculo)

        novo_item = {
            "nome": CliNome if CliNome != "TRATAMENTO" else "",
            "telefone": telefone if telefone != "TRATAMENTO" else "",
            "email": email if email != "TRATAMENTO" else "",
            "placa": placa if placa != "TRATAMENTO" else "",
            "marca": marca if marca != "TRATAMENTO" else "",
            "modelo": modelo if modelo != "TRATAMENTO" else "",
            "ano": ano if ano != "TRATAMENTO" else "",
            "motor": motor if motor != "TRATAMENTO" else "",
            "km": km if km != "TRATAMENTO" else "",
        }
        if len(cliente_os_atual["itens"]) == 0:
            cliente_os_atual["itens"].append(novo_item)
        else:
            cliente_os_atual["itens"][0] = novo_item
        servico.user_os_id = user.id
        servico.data_criado = datetime.now(timezone.utc).astimezone()
        servico.data_finalizada = datetime.now(timezone.utc).astimezone()
        servico.cliente_veiculo = json.dumps(cliente_os_atual)
        db.session.commit()
        return jsonify({"message": "Item atualizado com sucesso"})
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/EscolhaCliente/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def EscolhaCliente(id):
    try:
        get_serviso = Serviso.query.get_or_404(id)
        page = request.args.get("page", 1, type=int)
        clientes = Cliente.query.order_by(Cliente.id.desc()).paginate(
            page=page, per_page=10
        )
        veiculos = Veiculo.query.all()
        return render_template(
            "Clientes/cliente.html",
            Adicionar=get_serviso,
            clientes=clientes,
            veiculos=veiculos,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchAdicionarCliente", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def searchAdicionarCliente():
    try:
        if request.method == "POST":
            id = request.form.get("id")
            get_serviso = Serviso.query.get_or_404(id)
            veiculos = Veiculo.query.all()
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "placa":
                veiculos = Veiculo.query.filter(Veiculo.placa.like(search)).all()
                cliente_ids = [veiculo.cliente_id for veiculo in veiculos]
                clientes = (
                    Cliente.query.filter(Cliente.id.in_(cliente_ids))
                    .order_by(Cliente.id.desc())
                    .paginate(page=page, per_page=10)
                )
            elif escolha == "modelo":
                carros = Carro.query.filter(Carro.modelo.like(search)).all()
                idcarro = [carro.id for carro in carros]
                veiculos = Veiculo.query.filter(Veiculo.carro_id.in_(idcarro)).all()
                cliente_ids = [veiculo.cliente_id for veiculo in veiculos]
                clientes = (
                    Cliente.query.filter(Cliente.id.in_(cliente_ids))
                    .order_by(Cliente.id.desc())
                    .paginate(page=page, per_page=10)
                )
            elif escolha == "id":
                search_value = form["search_string"]
                search = "{0}".format(search_value)
                clientes = (
                    Cliente.query.filter(getattr(Cliente, escolha).like(search))
                    .order_by(Cliente.id.desc())
                    .paginate(page=page, per_page=10)
                )
            elif escolha == "email":
                search_va = form["search_string"]
                sear = "%{0}%".format(search_va)
                clientes = (
                    Cliente.query.filter(getattr(Cliente, escolha).like(sear))
                    .order_by(Cliente.id.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                clientes = (
                    Cliente.query.filter(getattr(Cliente, escolha).like(search))
                    .order_by(Cliente.id.desc())
                    .paginate(page=page, per_page=10)
                )

            return render_template(
                "/Clientes/cliente.html",
                Adicionar=get_serviso,
                clientes=clientes,
                veiculos=veiculos,
                busca=busca,
                escolha=escolha,
            )
        else:
            return redirect("/EscolhaCliente")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route(
    "/adicinar_cliente_os/<int:Ser_id>/<string:cli_id>", methods=["POST", "ADICIONAR"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def adicinar_cliente_os(Ser_id, cli_id):
    try:
        user = current_user
        servico = Serviso.query.get(Ser_id)
        if not servico:
            flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
        if servico.id != 0 and servico.status == "Finalizado":
            return redirect(f"/AbrirServiço/{servico.id}/tratatar")
        else:
            servico.cliente_os_id = cli_id
            servico.user_os_id = user.id
            servico.veiculo_os_id = 0
            servico.data_criado = datetime.now(timezone.utc).astimezone()
            servico.data_finalizada = datetime.now(timezone.utc).astimezone()
            db.session.commit()
            flash(f"Cliente Adicionado no {servico.status}!!!", "cor-ok")
            if servico.status == "Editar":
                return redirect(f"/finalizarEdit/{servico.id}/Editar")
            else:
                return redirect(f"/AbrirServiço/{servico.id}/tratatar")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Colocar Veiculo no Serviço
@app.route(
    "/EscolhaVeiculo/<int:servico_id>/<int:cli_id>", methods=["POST", "ADICIONAR"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def EscolhaVeiculo(servico_id, cli_id):
    try:
        get_serviso = Serviso.query.get_or_404(servico_id)
        veiculos = Veiculo.query.filter_by(cliente_id=cli_id).all()
        if get_serviso.id != 0 and get_serviso.status == "Finalizado":
            return redirect(f"/AbrirServiço/{get_serviso.id}/tratatar")
        else:
            if len(veiculos) == 0:
                flash("Não a Veiculo registrado para esse Cliente!!!", "cor-alerta")
                if get_serviso.status == "Editar":
                    return redirect(f"/finalizarEdit/{get_serviso.id}/Editar")
                else:
                    return redirect(f"/AbrirServiço/{get_serviso.id}/tratatar")
            elif len(veiculos) == 1:
                for a in veiculos:
                    get_serviso.veiculo_os_id = a.id
                    db.session.commit()
                flash("Veiculo Adicionado no Orçamento!!!", "cor-ok")
                if get_serviso.status == "Editar":
                    return redirect(f"/finalizarEdit/{get_serviso.id}/Editar")
                else:
                    return redirect(f"/AbrirServiço/{get_serviso.id}/tratatar")
            else:
                return render_template(
                    "Serviços/AddVeiculoServ.html",
                    get_serviso=get_serviso,
                    veiculos=veiculos,
                )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route(
    "/adicinar_veiculo_os/<int:Ser_id>/<string:veic_id>", methods=["POST", "ADICIONAR"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def adicinar_veiculo_os(Ser_id, veic_id):
    try:
        servico = Serviso.query.get(Ser_id)
        if not servico:
            flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
        if servico.id != 0 and servico.status == "Finalizado":
            return redirect(f"/AbrirServiço/{servico.id}/tratatar")
        else:
            servico.veiculo_os_id = veic_id
            db.session.commit()
            flash(f"Veiculo Adicionado no {servico.status}!!!", "cor-ok")
            if servico.status == "Editar":
                return redirect(f"/finalizarEdit/{servico.id}/Editar")
            else:
                return redirect(f"/AbrirServiço/{servico.id}/tratatar")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/retirarVeiculo/<int:servico_id>", methods=["POST", "DELETE"])
@login_required
@nome_required
@verificacao_nivel(2)
def retirarVeiculo(servico_id):
    try:
        servico = Serviso.query.get(servico_id)
        if not servico:
            flash(
                f"Algo deu Errado Consulte o Desenvovedor!!!",
                "cor-cancelar",
            )
        if servico.id != 0 and servico.status == "Finalizado":
            return redirect(f"/AbrirServiço/{servico.id}/tratatar")
        else:
            veiculo_os_atual = json.loads(servico.veiculo)

            veiculo_os_atual["itens"].pop(0)
            servico.veiculo = json.dumps(veiculo_os_atual)

            db.session.commit()
            if servico.status == "Finalizado":
                return redirect(f"/finalizarEdit/{servico.id}")
            else:
                return redirect(f"/AbrirServiço/{servico.id}/tratatar")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Atualizar OBSERVAÇÂO
@app.route(
    "/atualizar_obs_os/<int:Ser_id>/<string:obs>",
    methods=["PUT"],
)
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_obs_os(Ser_id, obs):
    if obs == "TRATAMENTO":
        obs = ""
    servico = Serviso.query.get(Ser_id)
    if not servico:
        flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
    if servico.id != 0 and servico.status == "Finalizado":
        pass
    else:
        servico.obs = obs
        db.session.commit()
    return jsonify({"message": "Item atualizado com sucesso"})


# Atualizar VENDEDOR
@app.route(
    "/atualizar_vendedor_os/<int:Ser_id>/<string:vendedor>",
    methods=["PUT"],
)
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_vendedor_os(Ser_id, vendedor):
    servico = Serviso.query.get(Ser_id)
    if not servico:
        flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
    if servico.id != 0 and servico.status == "Finalizado":
        pass
    else:
        servico.vendedor_id = vendedor
        db.session.commit()
    return jsonify({"message": "Item atualizado com sucesso"})


# Atualizar mecanico
@app.route(
    "/atualizar_mecanico_os/<int:Ser_id>/<string:mecanico>",
    methods=["PUT"],
)
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_mecanico_os(Ser_id, mecanico):
    servico = Serviso.query.get(Ser_id)
    if not servico:
        flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
    if servico.id != 0 and servico.status == "Finalizado":
        pass
    else:
        servico.mecanico_id = mecanico
        db.session.commit()
    return jsonify({"message": "Item atualizado com sucesso"})


# SERVIÇOS APROVADOS
@app.route("/aprovarServiço/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def aprovarServiço(id):
    try:
        servisoAprovado = Serviso.query.get_or_404(id)
        if servisoAprovado.status == "Aprovado":
            return redirect(f"/AbrirServiço/{servisoAprovado.id}/tratatar")
        peças_os = json.loads(servisoAprovado.peça_os)
        mos_os = json.loads(servisoAprovado.mo_os)
        getPeça = Peça.query.order_by(Peça.id)
        getMaoobra = Maoobra.query.order_by(Maoobra.id)
        if servisoAprovado.cliente_os_id > 0 and servisoAprovado.veiculo_os_id > 0:
            if request.method == "POST":
                for peça_um in getPeça:
                    if "itens" in peças_os:
                        for index, item in enumerate(peças_os["itens"]):
                            peça_id = item.get("peça_id")
                            if peça_um.id == peça_id:
                                peças_os["itens"][index]["valor_final"] = peça_um.preso
                                peças_os["itens"][index]["peça_codigo"] = peça_um.codigo
                                peças_os["itens"][index]["peça_nome"] = peça_um.nome
                                servisoAprovado.peça_os = json.dumps(peças_os)
                                db.session.commit()
                for mo_um in getMaoobra:
                    if "itens" in mos_os:
                        for index, item in enumerate(mos_os["itens"]):
                            mo_id = item.get("MDO_id")
                            if mo_um.id == mo_id:
                                mos_os["itens"][index]["MDO_preso"] = mo_um.preso
                                mos_os["itens"][index][
                                    "MDO_nome"
                                ] = mo_um.nomemaoobra.nome
                                servisoAprovado.mo_os = json.dumps(mos_os)

                                db.session.commit()
                if len(peças_os["itens"]) > 0:
                    for peça_um in getPeça:
                        for index, item in enumerate(peças_os["itens"]):
                            peçaid = item.get("peça_id")
                            peçaUn = item.get("un")
                            if peçaid == peça_um.id:
                                peça_modificar = Peça.query.get_or_404(peça_um.id)
                                if peça_modificar.estoque != 0:
                                    valor_atual = int(peça_modificar.estoque) - int(
                                        peçaUn
                                    )
                                    valor_estoque = 0
                                    if int(peça_modificar.estoque) > int(peçaUn):
                                        valor_estoque = peçaUn
                                    else:
                                        valor_estoque = peça_modificar.estoque
                                    if valor_atual < 0:
                                        valor_atual = 0
                                    peça_modificar.estoque = valor_atual

                                    db.session.commit()
                                    peça_os_atual = json.loads(servisoAprovado.peça_os)
                                    peça_os_atual["itens"][index][
                                        "em_estoque"
                                    ] = valor_estoque
                                    servisoAprovado.peça_os = json.dumps(peça_os_atual)
                                    db.session.commit()
                km = request.form.get("kmAtualiza")
                veiculo = Veiculo.query.get_or_404(servisoAprovado.veiculo_os_id)
                veiculo.km = km
                db.session.commit()
                servisoAprovado.status = "Aprovado"
                db.session.commit()
                flash(
                    f"O Serviço foi Aprovado, com Sucesso!!!",
                    "cor-ok",
                )
                return redirect(f"/AbrirServiço/{servisoAprovado.id}/tratatar")
            flash(f"{servisoAprovado.id}", "Aprovado")
            return redirect(f"/AbrirServiço/{servisoAprovado.id}/tratatar")
        else:
            flash(
                f"Para Aprovar o serviço, é necessário adicionar um cliente e veiculo do sistema.",
                "cor-alerta",
            )
            return redirect(f"/AbrirServiço/{servisoAprovado.id}/dados")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# SERVIÇOS FINALIZAR
@app.route("/finalizarServiço/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def finalizarServiço(id):
    servisoFinalizado = Serviso.query.get_or_404(id)
    if servisoFinalizado.status == "Finalizado":
        return redirect(f"/AbrirServiço/{servisoFinalizado.id}/tratatar")
    if servisoFinalizado.cliente_os_id > 0 and servisoFinalizado.veiculo_os_id > 0:
        if servisoFinalizado.vendedor_id >= 1 and servisoFinalizado.mecanico_id >= 1:
            if request.method == "POST":
                valor_recebido = request.form.getlist("pago")
                carteira = request.form.getlist("carteira")
                detalesPago = request.form.getlist("detalesPago")
                carteira_valores = json.loads(servisoFinalizado.carteira_id)
                vinda_pagamento = []
                if len(valor_recebido) == len(carteira) == len(detalesPago):
                    for i in range(len(valor_recebido)):
                        pago = valor_recebido[i]
                        carteira_atual = carteira[i]
                        detales_pago = detalesPago[i].upper()
                        limpa_valor = Calculos_gloabal.valor_para_Calculos(pago)
                        vinda_pagamento.append(limpa_valor)
                        novo_item = {
                            "carteira_id": carteira_atual,
                            "valor_recebido": pago,
                            "detalesPago": detales_pago,
                            }
                        carteira_valores["itens"].append(novo_item)
                        servisoFinalizado.carteira_id = json.dumps(carteira_valores)
                    db.session.commit()
                soma_vindo_carteiras = sum(vinda_pagamento)
                soma_vindo_carteiras_format =Calculos_gloabal.format_valor_moeda(soma_vindo_carteiras)

                km = request.form.get("kmAtualiza")

                valor_gasto = request.form.get("gasto")
                if not valor_gasto:
                    valor_gasto = '0,00'
                valor_pesas = request.form.get("valordaspesas")
                valor_total = request.form.get("valortodos")
                valor_mdo = Calculos_gloabal.valor_para_Calculos(
                    valor_total
                ) - Calculos_gloabal.valor_para_Calculos(valor_pesas)
                

                desconto_sobra =  soma_vindo_carteiras - Calculos_gloabal.valor_para_Calculos(
                    valor_total)
                desconto_sobra = Calculos_gloabal.format_valor_moeda(desconto_sobra)

                valor_pesas_soma = Calculos_gloabal.valor_para_Calculos(
                    valor_pesas
                ) - Calculos_gloabal.valor_para_Calculos(valor_gasto) + Calculos_gloabal.valor_para_Calculos(desconto_sobra)

                if valor_pesas_soma < 0:
                    valor_pesas_soma = 0
                
                if valor_pesas_soma < 0:
                    valor_pesas_soma = 0
                
                veiculo = Veiculo.query.get_or_404(servisoFinalizado.veiculo_os_id)
                veiculo.km = km
                db.session.commit()

                soma_ganho = soma_vindo_carteiras - Calculos_gloabal.valor_para_Calculos(valor_gasto)
                soma_ganho_form = Calculos_gloabal.format_valor_moeda(soma_ganho)
                if valor_mdo > soma_ganho:
                    valor_mdo = soma_ganho
                if soma_ganho < 0:
                    valor_mdo = 0
                    valor_pesas_soma_forma = 0

                valor_pesas_soma_forma = Calculos_gloabal.format_valor_moeda(valor_pesas_soma)
                valor_mdo = Calculos_gloabal.format_valor_moeda(valor_mdo)

                servisoFinalizado.km_final = km
                servisoFinalizado.valor_pesas = valor_pesas_soma_forma
                servisoFinalizado.valor_mdo = valor_mdo
                servisoFinalizado.valor_gasto = valor_gasto
                servisoFinalizado.valor_recebido = soma_vindo_carteiras_format
                servisoFinalizado.valor_total = valor_total
                servisoFinalizado.desconto_sobra = desconto_sobra
                servisoFinalizado.valor_ganho = soma_ganho_form
                servisoFinalizado.status = "Finalizado"
                servisoFinalizado.data_finalizada = datetime.now(
                    timezone.utc
                ).astimezone()
                db.session.commit()

                if len(valor_recebido) == len(carteira) == len(detalesPago):
                    for i in range(len(valor_recebido)):
                        pago = valor_recebido[i]
                        carteira_atual = carteira[i]
                        detales_pago = detalesPago[i].upper()
                        novo_caixa = Caixa(
                            pagopor=servisoFinalizado.id,
                            descricao=detales_pago,
                            valor=pago,
                            tipo="Entrada",
                            carteira_id=int(carteira_atual),
                            catcaixa_id=1,
                            fornecedor_id=0,
                            data_criado=datetime.now(timezone.utc).astimezone(),
                        )
                        db.session.add(novo_caixa)
                db.session.commit()
                flash(
                    f"O Serviço foi Finalizado, com Sucesso!!!",
                    "cor-ok",
                )
                return redirect(f"/AbrirServiço/{servisoFinalizado.id}/tratatar")
            flash(f"{servisoFinalizado.id}", "Finalizado")
            return redirect(f"/AbrirServiço/{servisoFinalizado.id}/tratatar")
        else:
            flash(
                f"Para Aprovar o serviço, é necessário adicionar um Mecanico e Vendedor do sistema.",
                "cor-alerta",
            )
            return redirect(f"/AbrirServiço/{servisoFinalizado.id}/tratatar")
    else:
        flash(
            f"Para Aprovar o serviço, é necessário adicionar um cliente e veiculo do sistema.",
            "cor-alerta",
        )
        return redirect(f"/AbrirServiço/{servisoFinalizado.id}/tratatar")


@app.route("/finalizarEdit/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def finalizarEdit(id):
    if id == 0:
        return redirect(f"/AbrirServiço/0/Editar")
    else:
        servisos = Serviso.query.get_or_404(id)
        data_hora_atual = datetime.now()
        data_serv_buscar = data_hora_atual - timedelta(days=5*365, minutes=3)

        # Criar objeto datetime com a nova data
        data_hora_especifica = datetime(
            data_serv_buscar.year,
            data_serv_buscar.month,
            data_serv_buscar.day,
            data_serv_buscar.hour,
            data_serv_buscar.minute,
            data_serv_buscar.second,
        )
        filtro = Caixa.query.filter(
            (servisos.data_finalizada > data_hora_especifica)
        ).first()
        if filtro:
            filtro_0 = Serviso.query.filter(Serviso.id == 0).first()
            if filtro_0:
                data_atualizacao_finalizacao = filtro_0.data_atulizado_finalizado
                uma_hora_atras = datetime.now() - timedelta(minutes=3)
                if data_atualizacao_finalizacao <= uma_hora_atras:
                    filtro_0.notafiscal = servisos.notafiscal
                    filtro_0.status = 'Editar'
                    filtro_0.cliente_veiculo = servisos.cliente_veiculo
                    filtro_0.data_criado = servisos.data_criado
                    filtro_0.data_finalizada = servisos.data_finalizada
                    filtro_0.peça_os = servisos.peça_os
                    filtro_0.mo_os = servisos.mo_os
                    filtro_0.obs = servisos.obs
                    filtro_0.km_final = servisos.km_final
                    filtro_0.carteira_id = servisos.carteira_id
                    filtro_0.valor_pesas = servisos.valor_pesas
                    filtro_0.valor_mdo = servisos.valor_mdo
                    filtro_0.valor_gasto = servisos.valor_gasto
                    filtro_0.valor_recebido = servisos.valor_recebido
                    filtro_0.valor_total = servisos.valor_total
                    filtro_0.desconto_sobra = servisos.desconto_sobra
                    filtro_0.valor_ganho = servisos.valor_ganho
                    filtro_0.cliente_os_id = servisos.cliente_os_id
                    filtro_0.veiculo_os_id = servisos.veiculo_os_id
                    filtro_0.user_os_id = servisos.user_os_id
                    filtro_0.mecanico_id = servisos.mecanico_id
                    filtro_0.vendedor_id = servisos.vendedor_id
                    filtro_0.editor_finalizado_id = servisos.id
                    filtro_0.data_atulizado_finalizado = datetime.now(
                        timezone.utc
                    ).astimezone()
                    db.session.commit()
                else:
                    flash(
                        "No momento, não é possível modificar este registro. Por favor, aguarde pelo menos 3 minutos e tente novamente",
                        "cor-cancelar",
                    )
                    return redirect(f"/AbrirServiço/{id}/tratatar")
            else:
                get_Serviso = Serviso(
                    id=0,
                    notafiscal=servisos.notafiscal,
                    status=servisos.status,
                    cliente_veiculo=servisos.cliente_veiculo,
                    data_criado=servisos.data_criado,
                    data_finalizada=servisos.data_finalizada,
                    peça_os=servisos.peça_os,
                    mo_os=servisos.mo_os,
                    obs=servisos.obs,
                    km_final=servisos.km_final,
                    carteira_id=servisos.carteira_id,
                    valor_pesas=servisos.valor_pesas,
                    valor_mdo=servisos.valor_mdo,
                    valor_gasto=servisos.valor_gasto,
                    valor_recebido=servisos.valor_recebido,
                    valor_total=servisos.valor_total,
                    desconto_sobra=servisos.desconto_sobra,
                    cliente_os_id=servisos.cliente_os_id,
                    veiculo_os_id=servisos.veiculo_os_id,
                    user_os_id=servisos.user_os_id,
                    mecanico_id=servisos.mecanico_id,
                    vendedor_id=servisos.vendedor_id,
                    editor_finalizado_id=servisos.id,
                    data_atulizado_finalizado=datetime.now(timezone.utc).astimezone(),
                )
                db.session.add(get_Serviso)
                db.session.commit()

            return redirect(f"/AbrirServiço/0/Editar")
        else:
            flash(
                "Os serviços finalizados nos meses anteriores não podem ser modificados.",
                "cor-cancelar",
            )
            return redirect(f"/AbrirServiço/{id}/tratatar")


@app.route("/finalizarEditVolt/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def finalizarEditVolt(id):
    servisos = Serviso.query.get_or_404(id)
    if servisos.cliente_os_id > 0 and servisos.veiculo_os_id > 0:
        if servisos.vendedor_id >= 1 and servisos.mecanico_id >= 1:
            if request.method == "POST":
                servisoFinalizado = Serviso.query.get_or_404(
                    servisos.editor_finalizado_id
                )
                valor_recebido = request.form.getlist("pago")
                carteira = request.form.getlist("carteira")
                detalesPago = request.form.getlist("detalesPago")

                carteira_valores = json.loads(servisos.carteira_id)
                vinda_pagamento = []
                if len(valor_recebido) == len(carteira) == len(detalesPago):
                    for i in range(len(valor_recebido)):
                        pago = valor_recebido[i]
                        carteira_atual = carteira[i]
                        detales_pago = detalesPago[i].upper()
                        limpa_valor = Calculos_gloabal.valor_para_Calculos(pago)
                        vinda_pagamento.append(limpa_valor)
                        carteira_valores["itens"][i]["carteira_id"] = carteira_atual
                        carteira_valores["itens"][i]["valor_recebido"] = pago
                        carteira_valores["itens"][i]["detalesPago"] = detales_pago
                        servisoFinalizado.carteira_id = json.dumps(carteira_valores)
                    db.session.commit()
                soma_vindo_carteiras = sum(vinda_pagamento)
                soma_vindo_carteiras_format =Calculos_gloabal.format_valor_moeda(soma_vindo_carteiras)
                
                km = request.form.get("kmAtualiza")
                valor_gasto = request.form.get("gasto")
                if not valor_gasto:
                    valor_gasto = '0,00'
                valor_pesas = request.form.get("valordaspesas")
                valor_total = request.form.get("valortodos")
                
                valor_mdo = Calculos_gloabal.valor_para_Calculos(
                    valor_total
                ) - Calculos_gloabal.valor_para_Calculos(valor_pesas)


                desconto_sobra =  soma_vindo_carteiras - Calculos_gloabal.valor_para_Calculos(
                    valor_total)
                desconto_sobra = Calculos_gloabal.format_valor_moeda(desconto_sobra)

                valor_pesas_soma = Calculos_gloabal.valor_para_Calculos(
                    valor_pesas
                ) - Calculos_gloabal.valor_para_Calculos(valor_gasto) + Calculos_gloabal.valor_para_Calculos(desconto_sobra)
                if valor_pesas_soma < 0:
                    valor_pesas_soma = 0

                veiculo = Veiculo.query.get_or_404(servisos.veiculo_os_id)
                veiculo.km = km
                db.session.commit()

                soma_ganho = soma_vindo_carteiras - Calculos_gloabal.valor_para_Calculos(valor_gasto)

                if valor_mdo > soma_ganho:
                    valor_mdo = soma_ganho
                if soma_ganho < 0:
                    valor_mdo = 0
                    valor_pesas_soma_forma = 0

                valor_pesas_soma_forma = Calculos_gloabal.format_valor_moeda(valor_pesas_soma)
                valor_mdo = Calculos_gloabal.format_valor_moeda(valor_mdo)
                soma_ganho_form = Calculos_gloabal.format_valor_moeda(soma_ganho)
                
                servisoFinalizado.notafiscal = servisos.notafiscal
                servisoFinalizado.status = 'Finalizado'
                servisoFinalizado.cliente_veiculo = servisos.cliente_veiculo
                servisoFinalizado.data_finalizada = servisos.data_finalizada
                servisoFinalizado.peça_os = servisos.peça_os
                servisoFinalizado.mo_os = servisos.mo_os
                servisoFinalizado.obs = servisos.obs
                servisoFinalizado.km_final = km
                servisoFinalizado.valor_pesas = valor_pesas_soma_forma
                servisoFinalizado.valor_mdo = valor_mdo
                servisoFinalizado.valor_gasto = valor_gasto
                servisoFinalizado.valor_recebido = soma_vindo_carteiras_format
                servisoFinalizado.valor_total = valor_total
                servisoFinalizado.desconto_sobra = desconto_sobra
                servisoFinalizado.valor_ganho = soma_ganho_form
                servisoFinalizado.cliente_os_id = servisos.cliente_os_id
                servisoFinalizado.veiculo_os_id = servisos.veiculo_os_id
                servisoFinalizado.user_os_id = servisos.user_os_id
                servisoFinalizado.mecanico_id = servisos.mecanico_id
                servisoFinalizado.vendedor_id = servisos.vendedor_id
                servisoFinalizado.data_atulizado_finalizado = datetime.now(
                    timezone.utc
                ).astimezone()
                db.session.commit()

                caixa_atualize = Caixa.query.filter_by(pagopor=servisoFinalizado.id).all()
                for c, i in zip(caixa_atualize, range(len(valor_recebido))):
                    pago = valor_recebido[i]
                    carteira_atual = carteira[i]
                    detales_pago = detalesPago[i].upper()

                    c.pagopor = servisoFinalizado.id
                    c.descricao = detales_pago
                    c.valor = pago
                    c.carteira_id = int(carteira_atual)

                    db.session.commit()
                flash(
                    f"O Serviço foi Editar, com Sucesso!!!",
                    "cor-ok",
                )
                return redirect(f"/AbrirServiço/{servisoFinalizado.id}/tratatar")

        else:
            flash(
                f"Para Editar o serviço, é necessário adicionar um Mecanico e Vendedor do sistema.",
                "cor-alerta",
            )
            return redirect(f"/AbrirServiço/{servisos.id}/Editar")
    else:
        flash(
            f"Para Editar o serviço, é necessário adicionar um cliente e veiculo do sistema.",
            "cor-alerta",
        )
        return redirect(f"/AbrirServiço/{servisos.id}/Editar")


