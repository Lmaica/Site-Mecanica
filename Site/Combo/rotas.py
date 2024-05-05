from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    current_app,
    request,
    jsonify,
)
from Site import db, app,photos, nome_required, verificacao_nivel
from .modelos import Combo
from Site.Global.fun_global import Calculos_gloabal, Redutor_codigo
from Site.Pecas.modelos import Marcapeca, Peca
from Site.MaoObra.modelos import Maoobra, Catmaoobra, Nomemaoobra
from sqlalchemy import desc, and_, or_
import json
from flask_login import login_required, current_user
import os
import secrets
from Site.Fornecedor.modelos import Fornecedor
from Site.Global.fun_global import Calculos_gloabal, Redutor_codigo, Edit_global
from Site.Carros.modelos import Carro
from datetime import datetime, timedelta 
from Site.Servicos.modelos import Serviso

# Dados do Serviços 
@app.route("/combos", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def combos():
    try:
        page = request.args.get("page", 1, type=int)
        combos = Combo.query.order_by(desc(Combo.id)).paginate(page=page, per_page=10)
        return render_template(
            "Combo/combo.html",
            combos=combos,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addCombo", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def addCombo():
    dadosJson = {"itens": []}
    get_Combo = Combo(
        status="Normal",
        tipo="Basico",
        nome='',
        peca_os_combo=json.dumps(dadosJson),
        mo_os_combo=json.dumps(dadosJson),
        obs='',
        valor_total='',
        image_1='foto.jpg',
    )
    db.session.add(get_Combo)
    db.session.commit()
    filtro = Combo.query.order_by(desc(Combo.id)).first()
    getCombo = filtro
    return redirect(f"/AbrirCombo/{getCombo.id}")


@app.route("/searchCombo", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def searchCombo():
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "todos":
                search_terms = search.split()  
                conditions = []
                for term in search_terms:
                    conditions.append(
                        or_(
                            Combo.id.like(f'%{term}%'),
                            Combo.nome.like(f'%{term}%'),
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
            else:
                get_combos = (
                    Combo.query.filter(getattr(Combo, escolha).like(search))
                    .filter(Combo.id != 0)
                    .order_by(Combo.data_inicil_combo.desc())
                    .paginate(page=page, per_page=10)
                )
            return render_template(
                "Combo/combo.html",
                combos=get_combos,
                busca=busca,
                escolha=escolha,
            )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deleteCombos/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteCombos(id):
    try:
        getCombo = Combo.query.get_or_404(id)
        if request.method == "POST":
            try:
                db.session.delete(getCombo)
                db.session.commit()
                try:
                    if getCombo.image_1 != "foto.jpg":
                        os.remove(
                            os.path.join(
                                current_app.root_path, "static/imagens/" + getCombo.image_1
                            )
                        )
                    else:
                        pass
                except Exception as e:
                    pass
                flash(
                    f"A Peça foi Deletada com Sucesso!!!",
                    "cor-ok",
                )
                return jsonify()
            except:
                flash(
                    f"A Peça Não pode ser APAGADO, Ao invés de apagar Modifique, pois a Serviços cadastrados com essa Peça!",
                    "cor-alerta",
                )
                return jsonify()
        flash(f"A Peça NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/AbrirCombo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def AbrirCombo(id):
    data_atual = datetime.now()
    get_combo = Combo.query.get_or_404(id)
    
    if (("itens" in get_combo.peca_os_combo and json.loads(get_combo.peca_os_combo)["itens"]) or ("itens" in get_combo.mo_os_combo and json.loads(get_combo.mo_os_combo)["itens"])) and get_combo.nome != '' and get_combo.obs != '' and get_combo.carro != '""' and get_combo.image_1 != 'foto.jpg' and get_combo.data_inicil_combo < data_atual and (get_combo.data_final_combo is None or get_combo.data_final_combo > data_atual):
        get_combo.atividade = 'Ativo'
    else:
        get_combo.atividade = None
    db.session.commit()
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
    
    return render_template(
        "/Combo/addCombo.html",
        Combo=get_combo,
        items_data_pecas=items_data_pecas,
        items_data_MDO=items_data_MDO,
        marcas=marcas,
    )


@app.route("/addComboServico/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def addComboServico(id):
    get_serviso = Serviso.query.get_or_404(id)
    get_carro=get_serviso.veiculo_os.carro.marca +' '+ get_serviso.veiculo_os.carro.modelo
    get_Combo = Combo(
        status="Normal",
        tipo="Basico",
        carro=get_carro,
        nome='',
        peca_os_combo=get_serviso.peca_os,
        mo_os_combo=get_serviso.mo_os,
        obs='',
        image_1='foto.jpg',
    )
    db.session.add(get_Combo)
    db.session.commit()
    filtro = Combo.query.order_by(desc(Combo.id)).first()
    getCombo = filtro
    return redirect(f"/AbrirCombo/{getCombo.id}")

@app.route("/duplicarCombo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def duplicarCombo(id):
    get_combo = Combo.query.get_or_404(id)
    get_Combo = Combo(
        status="Normal",
        tipo="Basico",
        carro=get_combo.carro,
        nome=get_combo.nome,
        peca_os_combo=get_combo.peca_os_combo,
        mo_os_combo=get_combo.mo_os_combo,
        obs='',
        image_1='foto.jpg',
    )
    db.session.add(get_Combo)
    db.session.commit()
    filtro = Combo.query.order_by(desc(Combo.id)).first()
    getCombo = filtro
    return redirect(f"/AbrirCombo/{getCombo.id}")

# Pecas do Serviços
@app.route("/AddItensManualCombo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def AddItensManualCombo(id):
    try:
        get_Combo = Combo.query.get_or_404(id)
        if request.method == "POST":
            tipo = request.form.get("tipo")
            codigo = request.form.get("Codigo").upper()
            NomeItens = request.form.get("NomeItens").upper()
            unidad = request.form.get("unidad")
            lado = request.form.get("lado")
            custo = request.form.get("custo")
            venda = request.form.get("venda")
            codigo = '*' +  codigo
            if tipo == 'Peca':
                peca_os_atual = json.loads(get_Combo.peca_os_combo)
                novo_item = {
                    "peca_id": 0,
                    "peca_codigo": codigo,
                    "peca_nome": NomeItens,
                    "un": unidad,
                    "lado": lado,
                    "em_estoque": 0,
                    "valor_custo": custo,
                    "valor_final": venda,
                }
                peca_os_atual["itens"].append(novo_item)
                get_Combo.peca_os_combo = json.dumps(peca_os_atual)
            else: 
                MaoObra_os_atual = json.loads(get_Combo.mo_os_combo)
                novo_item = {
                    "MDO_id": 0,
                    "MDO_nome": NomeItens,
                    "MDO_preso": venda,
                }
                MaoObra_os_atual["itens"].append(novo_item)
                get_Combo.mo_os_combo = json.dumps(MaoObra_os_atual)
            db.session.commit()
            return redirect(f"/AbrirCombo/{get_Combo.id}")
        flash(f"{get_Combo.id}", "itensCombo")
        return redirect(f"/AbrirCombo/{get_Combo.id}")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

@app.route("/EscolhaPecasCombo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def EscolhaPecasCombo(id):
    try:
        get_Combo = Combo.query.get_or_404(id)
        page = request.args.get("page", 1, type=int)
        getPeca = Peca.query.order_by(Peca.id.desc()).paginate(page=page, per_page=10)
        CatPeca = Marcapeca.query.all()
        fornecedors = Fornecedor.query.all()
        return render_template(
            "/Pecas/Peca.html",
            AdicionarCombo=get_Combo,
            Pecas=getPeca,
            marcas=CatPeca,
            fornecedors=fornecedors,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route(
    "/adicinar_item_peca_combo", methods=["PUT"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def adicinar_item_peca_combo():
    id_Combo = request.form.get("numero_Combo")
    id_peca = request.form.get("numero_peca")
    get_Combo = Combo.query.get_or_404(id_Combo)

    getPeca = Peca.query.get_or_404(id_peca)
    numero = request.form.get("unidad")
    lado = request.form.get("lado")
    peca_os_combo_atual = json.loads(get_Combo.peca_os_combo)
    if not Combo:
        return "Combo não encontrado", 404
    if len(peca_os_combo_atual["itens"]) > 0:
        for item in peca_os_combo_atual["itens"]:
            pecaid = item.get("peca_id")
            if pecaid == getPeca.id:
                flash=f"A Peça com ID {getPeca.id} Já foi adicionado ao Orçamento!!!"
                response_data = {
                    "success": True,
                    "message": flash,
                    "cor": "cor-alerta",
                }
                return jsonify(response_data)
    valor_estoque = 0
    novo_item = {
        "peca_id": getPeca.id,
        "peca_codigo": getPeca.codigo,
        "peca_nome": getPeca.nome,
        "un": numero,
        "lado": lado,
        "em_estoque": valor_estoque,
        "valor_custo": getPeca.pago,
        "valor_final": getPeca.preso,
    }
    peca_os_combo_atual["itens"].append(novo_item)
    get_Combo.peca_os_combo = json.dumps(peca_os_combo_atual)

    db.session.commit()
    flash = f"A Peça foi Adicionada com Sucesso!!!"
    
    response_data = {
        "success": True,
        "message": flash,
        "cor": "cor-ok",
    }
    return jsonify(response_data)


@app.route("/atualizar_uni_pecas_combo/<int:Combo_id>/<int:item_id>", methods=["PUT"])
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_uni_pecas_combo(Combo_id, item_id):
    try:
        
        quantity = int(request.form.get("un"))
        getCombo = Combo.query.get(Combo_id)
        if not getCombo:
            flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
        else:
            peca_os_combo_atual = json.loads(getCombo.peca_os_combo)

            if item_id < 0 or item_id >= len(peca_os_combo_atual.get("itens", [])):
                flash(
                    "Índice do item inválido. Consulte o Desenvolvedor!!!",
                    "cor-cancelar",
                )
            peca_os_combo_atual["itens"][item_id]["un"] = quantity
            getCombo.peca_os_combo = json.dumps(peca_os_combo_atual)
            db.session.commit()
        return jsonify({"message": "Item atualizado com sucesso"})
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atualizar_lado_pecas_combo/<int:Combo_id>/<int:item_id>", methods=["PUT"])
@login_required
@nome_required
@verificacao_nivel(2)
def atualizar_lado_pecas_combo(Combo_id, item_id):
    getCombo = Combo.query.get(Combo_id)
    lado = str(request.form.get("lado"))
    if not getCombo:
        flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
    else:
        peca_os_combo_atual = json.loads(getCombo.peca_os_combo)

        if item_id < 0 or item_id >= len(peca_os_combo_atual.get("itens", [])):
            flash(
                "Índice do item inválido. Consulte o Desenvolvedor!!!", "cor-cancelar"
            )

        peca_os_combo_atual["itens"][item_id]["lado"] = lado

        getCombo.peca_os_combo = json.dumps(peca_os_combo_atual)

        db.session.commit()

    return jsonify({"message": "Item atualizado com sucesso"})


@app.route(
    "/apagar_item_pecas_combo/<int:Combo_id>/<int:item_index>", methods=["POST", "DELETE"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def apagar_item_pecas_combo(Combo_id, item_index):
    try:
        getCombo = Combo.query.get(Combo_id)
        if not getCombo:
            flash(
                f"Algo deu Errado Consulte o Desenvovedor!!!",
                "cor-cancelar",
            )
        if getCombo.id != 0 and getCombo.status == "Finalizado":
            return redirect(f"/AbrirCombo/{getCombo.id}/tratatar")
        else:
            peca_os_combo_atual = json.loads(getCombo.peca_os_combo)
            if item_index < 0 or item_index >= len(peca_os_combo_atual.get("itens", [])):
                flash(
                    f"Algo deu Errado Consulte o Desenvovedor!!!",
                    "cor-cancelar",
                )
            peca_os_combo_atual["itens"].pop(item_index)
            getCombo.peca_os_combo = json.dumps(peca_os_combo_atual)

            db.session.commit()

            return redirect(f"/AbrirCombo/{getCombo.id}")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchPecasAdicionarCombo", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def searchPecasAdicionarCombo():
    try:
        if request.method == "POST":
            id = request.form.get("id")
            get_Combo = Combo.query.get_or_404(id)
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "marca":
                get_Pecas = Peca.query.filter(
                    Peca.marca.has(Marcapeca.nome.like(search))
                ).paginate(page=page, per_page=4)
            elif escolha == "fornecedor":
                get_Pecas = Peca.query.filter(
                    Peca.fornecedor.has(Fornecedor.nome.like(search))
                ).paginate(page=page, per_page=4)
            elif escolha == "todos":
                search_terms = search.split()  
                conditions = []
                for term in search_terms:
                    conditions.append(
                        or_(
                            Peca.id.like(f'%{term}%'),
                            Peca.codigo.like(f'%{term}%'),
                            Peca.codigo_debarra.like(f'%{term}%'),
                            Peca.nome.like(f'%{term}%'),
                            Peca.pago.like(f'%{term}%'),
                            Peca.preso.like(f'%{term}%'),
                            Peca.estoque.like(f'%{term}%'),
                            Peca.carro.like(f'%{term}%'),
                            Peca.descrisao.like(f'%{term}%'),
                            Peca.data_criado.like(f'%{term}%'),
                            Peca.marca.has(Marcapeca.nome.like(f'%{term}%')),
                            Peca.fornecedor.has(Fornecedor.nome.like(f'%{term}%')),
                        )
                    )
                get_Pecas = (
                    Peca.query.filter(
                        *conditions
                    )
                    .order_by(Peca.id.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                get_Pecas = (
                    Peca.query.filter(getattr(Peca, escolha).like(search))
                    .order_by(Peca.id.desc())
                    .paginate(page=page, per_page=10)
                )
            marcaPesa = Marcapeca.query.all()
            return render_template(
                "Pecas/Peca.html",
                AdicionarCombo=get_Combo,
                Pecas=get_Pecas,
                busca=busca,
                escolha=escolha,
                CatPeca=marcaPesa,
            )
        else:
            return redirect("EscolhaMDOCombo")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Mao de obra Para Combo
@app.route("/EscolhaMDOCombo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def EscolhaMDOCombo(id):
    get_Combo = Combo.query.get_or_404(id)
    if request.method == "POST":
        MDOId = request.form.get("id")
        getMDO = Maoobra.query.get_or_404(MDOId)

        MDO_os_atual = json.loads(get_Combo.mo_os_combo)

        if not Combo:
            return "Combo não encontrado", 404

        novo_item = {
            "MDO_id": getMDO.id,
        }
        MDO_os_atual["itens"].append(novo_item)
        get_Combo.mo_os_combo = json.dumps(MDO_os_atual)

        db.session.commit()
        flash(
            f"A Mão de Obra foi Adicionada com Sucesso!!!",
            "cor-ok",
        )
        return redirect(f"/EscolhaMDOCombo/{get_Combo.id}")
    page = request.args.get("page", 1, type=int)
    MaoObras = Maoobra.query.order_by(Maoobra.id.desc()).paginate(
        page=page, per_page=10
    )
    CatMaoObra = Catmaoobra.query.all()
    NomeMaoObra = Nomemaoobra.query.all()
    return render_template(
        "MaoObras/maoObra.html",
        AdicionarCombo=get_Combo,
        MaoObras=MaoObras,
        NomeMaoObra=NomeMaoObra,
        CatMaoObra=CatMaoObra,
    )


@app.route(
    "/adicinar_item_MaoObra_Combo", methods=["PUT"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def adicinar_item_MaoObra_Combo():
    id_Combo = request.form.get("numero_Combo")
    id_mdo = request.form.get("numero_mdo")
    get_Combo = Combo.query.get_or_404(id_Combo)
    getMaoObra = Maoobra.query.get_or_404(id_mdo)
    MaoObra_os_atual = json.loads(get_Combo.mo_os_combo)

    if not Combo:
        return "Combo não encontrado", 404
    if get_Combo.id != 0 and get_Combo.status == "Finalizado":
        return redirect(f"/AbrirCombo/{get_Combo.id}/tratatar")
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
        get_Combo.mo_os_combo = json.dumps(MaoObra_os_atual)
        db.session.commit()
        flash="A Mão de Obra foi Adicionada com Sucesso!!!"
        response_data = {
                        "success": True,
                        "message": flash,
                        "cor": "cor-ok",
                    }
        return jsonify(response_data)


@app.route("/searchMDOAdicionarCombo", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(2)
def searchMDOAdicionarCombo():
    try:
        if request.method == "POST":
            id = request.form.get("id")
            get_Combo = Combo.query.get_or_404(id)
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
            elif escolha == "todos":
                search_terms = search.split()  
                conditions = []
                for term in search_terms:
                    conditions.append(
                        or_(
                            Maoobra.id.like(f'%{term}%'),
                            Maoobra.tempo.like(f'%{term}%'),
                            Maoobra.preso.like(f'%{term}%'),
                            Maoobra.marca.like(f'%{term}%'),
                            Maoobra.modelo.like(f'%{term}%'),
                            Maoobra.anoIni.like(f'%{term}%'),
                            Maoobra.anoFin.like(f'%{term}%'),
                            Maoobra.motor.like(f'%{term}%'),
                            Maoobra.nomemaoobra.has(Nomemaoobra.nome.like(f'%{term}%')),
                            Maoobra.catmaoobra.has(Catmaoobra.nome.like(f'%{term}%')),
                        )
                    )
                MaoObras = (
                    Maoobra.query.filter(
                        *conditions
                    )
                    .order_by(Maoobra.id.desc())
                    .paginate(page=page, per_page=10)
                )
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
                AdicionarCombo=get_Combo,
                MaoObras=MaoObras,
                busca=busca,
                escolha=escolha,
                NomeMaoObra=NomeMaoObra,
                CatMaoObra=CatMaoObra,
            )
        else:
            return redirect("/EscolhaMDOCombo")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route(
    "/apagar_item_mos_combo/<int:Combo_id>/<int:item_index>", methods=["POST", "DELETE"]
)
@login_required
@nome_required
@verificacao_nivel(2)
def apagar_item_mos_combo(Combo_id, item_index):
    try:
        getCombo = Combo.query.get(Combo_id)
        if not Combo:
            flash(
                f"Algo deu Errado Consulte o Desenvovedor!!!",
                "cor-cancelar",
            )
        else:
            mo_os_combo_atual = json.loads(getCombo.mo_os_combo)
            if item_index < 0 or item_index >= len(mo_os_combo_atual.get("itens", [])):
                flash(
                    f"Algo deu Errado Consulte o Desenvovedor!!!",
                    "cor-cancelar",
                )

            mo_os_combo_atual["itens"].pop(item_index)
            getCombo.mo_os_combo = json.dumps(mo_os_combo_atual)
            db.session.commit()
            return redirect(f"/AbrirCombo/{getCombo.id}")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Dados cliente Orçamento
@app.route("/dadosCombo/<int:Com_id>",methods=["PUT"])
@login_required
@nome_required
@verificacao_nivel(2)
def dadosCombo(Com_id):
    data_atual = datetime.now()
    atividade_combo = 0
    nome = request.form.get("nome").strip()
    totalInput = request.form.get("totalInput").strip()
    if nome == '':
        atividade_combo = 0
    else:
        atividade_combo += 1
    status = request.form.get("status")
    tipo = request.form.get("tipo")
    
    data_inicil_combo = request.form.get("data_inicil_combo")
    data_inicial_for = datetime.strptime(data_inicil_combo, "%Y-%m-%d")
    if data_inicial_for > data_atual:
        atividade_combo = 0
    else:
        atividade_combo += 1
    obs = request.form.get("obs").strip()
    if obs == '':
        atividade_combo = 0
    else:
        atividade_combo += 1

    carrosInput = request.form.get("carrosInput").strip()
    if carrosInput == '':
        atividade_combo = 0
    else:
        atividade_combo += 1
        
    data_final_combo = request.form.get("data_final_combo")
    if data_final_combo != '':
        data_fim_for = datetime.strptime(data_final_combo, "%Y-%m-%d")
        if data_fim_for > data_atual:
            atividade_combo += 1
        else:
            atividade_combo = 0
    else:
        data_fim_for = None
        atividade_combo += 1
    getCombo = Combo.query.get(Com_id)
    if not getCombo:
        flash("Algo deu Errado. Consulte o Desenvolvedor!!!", "cor-cancelar")
        return jsonify({"message": "Erro ao atualizar o item"})
    
    imagem = request.files.get("image_1")

    if imagem != None:
        if getCombo.image_1 != "foto.jpg":
            try:
                os.unlink(
                    os.path.join(
                        current_app.root_path,
                        "static/imagens/" + getCombo.image_1,
                    )
                )
                getCombo.image_1 = photos.save(
                    request.files.get("image_1"),
                    name=secrets.token_hex(10) + "...",
                )
                atividade_combo += 1
            except:
                getCombo.image_1 = "foto.jpg"
                atividade_combo = 0
        else:
            try:
                getCombo.image_1 = photos.save(
                    request.files.get("image_1"),
                    name=secrets.token_hex(10) + "...",
                )
                atividade_combo += 1
            except Exception as e:
                getCombo.image_1 = "foto.jpg"
                atividade_combo = 0
    if getCombo.image_1 == 'foto.jpg':
        atividade_combo = 0
    else:
        atividade_combo += 1

    if ("itens" in getCombo.peca_os_combo and json.loads(getCombo.peca_os_combo)["itens"]) or ("itens" in getCombo.mo_os_combo and json.loads(getCombo.mo_os_combo)["itens"]):
        atividade_combo += 1
    else:
        atividade_combo = 0
        
    if atividade_combo >= 7:
        getCombo.atividade = 'Ativo'
    else:
        getCombo.atividade = None 

    getCombo.nome = nome.upper()
    getCombo.status = status 
    getCombo.tipo = tipo 
    getCombo.valor_total = totalInput 
    getCombo.data_inicil_combo = data_inicial_for
    getCombo.data_final_combo = data_fim_for
    getCombo.obs = obs
    getCombo.carro = carrosInput 
    db.session.commit()
    return jsonify({"message": getCombo.atividade})
