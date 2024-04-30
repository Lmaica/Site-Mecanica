from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    request,
    jsonify,
)
from .formolarios import AddCaixas
from Site import db, app, nome_required, verificacao_nivel
from Site.Global.fun_global import Redutor_codigo, Calculos_gloabal
from .modelos import Carteirabanco, Caixa, Catcaixa
from Site.Fornecedor.modelos import Fornecedor
from datetime import datetime, timezone
from sqlalchemy import and_
from flask_login import login_required
from sqlalchemy import or_


@app.route("/Categorias_de_Caixa")
@login_required
@nome_required
@verificacao_nivel(4)
def Categorias_de_Caixa():
    try:
        page = request.args.get("page", 1, type=int)
        catcaixa = Catcaixa.query.order_by(Catcaixa.id.desc()).paginate(
            page=page, per_page=10
        )
        return render_template(
            "/umDado.html",
            perfils=catcaixa,
            perfil="Categorias_de_Caixa",
            produto="Categorias de Caixa",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addCategorias_de_Caixa", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addCategorias_de_Caixa():
    return Redutor_codigo.handle_generic_add(
        request, Catcaixa, "nome", "Categorias_de_Caixa"
    )


@app.route("/atulizCategorias_de_Caixa/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def atulizCategorias_de_Caixa(id):
    if id == 1 or id == 2:
        flash(f"A Categoria, Não pode ser Editada!!!", "cor-cancelar")
        return redirect(url_for("Categorias_de_Caixa"))
    return Redutor_codigo.handle_generic_update(
        request, Catcaixa, id, "nome", "Categorias_de_Caixa"
    )


@app.route("/deleteCategorias_de_Caixa/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteCategorias_de_Caixa(id):
    if id == 1 or id == 2:
        flash(f"A Categoria, Não pode ser Deletada!!!", "cor-cancelar")
        return jsonify()
    return Redutor_codigo.handle_generic_delete(
        request, Catcaixa, id, "nome", "Categorias_de_Caixa"
    )


@app.route("/searchCategorias_de_Caixa", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def searchCategorias_de_Caixa():
    return Redutor_codigo.search_generic(Catcaixa, "Categorias_de_Caixa")


# Carteiras

@app.route('/trasferir/<int:id>', methods=['GET', 'POST'])
@login_required
@nome_required
@verificacao_nivel(4)
def trasferir(id):
    getCaixas = Caixa.query.all()
    carteiraTrasferir = Carteirabanco.query.filter_by(id=id).first()
    lista_de_valores = []
    carteira_id_saida = []
    caixa_id_entrada = []
    contador = 0
    for cartera_caixas in getCaixas:
        contador += 1
        valor_calculado = Calculos_gloabal.valor_para_Calculos(cartera_caixas.valor)
        if carteiraTrasferir.id == cartera_caixas.carteira_id:
            if cartera_caixas.tipo == "Saida":
                carteira_id_saida.append(valor_calculado)
            else:
                caixa_id_entrada.append(valor_calculado)
        somar_entrada = sum(caixa_id_entrada)
        somar_saida = sum(carteira_id_saida)
        somas_total = somar_entrada - somar_saida
        somas_total_sistema = somas_total
        somas_total = Calculos_gloabal.format_valor_moeda(somas_total)

        if contador == len(getCaixas):
            lista_de_valores.append(
                {
                    "id": carteiraTrasferir.id,
                    "nome": carteiraTrasferir.nome,
                    "valor": somas_total,
                }
            )
    if somas_total_sistema <= 0:
        flash('Saldo Insuficiente na Carteira!', 'cor-cancelar')
        return redirect(url_for("Carteiras"))
    carteiras = Carteirabanco.query.filter(Carteirabanco.id != carteiraTrasferir.id).all()
    if request.method == "POST":
        conta_destino = request.form.get("conta_destino")
        motivo = request.form.get("motivo")
        valor_transferido = request.form.get("valor")
        valor_transferido_sistema = Calculos_gloabal.valor_para_Calculos(valor_transferido)
        if somas_total_sistema < valor_transferido_sistema:
            flash('Saldo Insuficiente na Carteira!', 'cor-cancelar')
            return render_template(
                "Caixa/trasferir.html",
                carteiras=carteiras,
                lista_de_valores=lista_de_valores,
            )
        novo_caixa_saida = Caixa(
                pagopor='TRANSFERÊNCIA',
                descricao=motivo,
                valor=valor_transferido,
                tipo='Saida',
                carteira_id=carteiraTrasferir.id,
                catcaixa_id=2,
                fornecedor_id=0,
                data_criado=datetime.now(timezone.utc).astimezone(),
            )
        novo_caixa_entrada = Caixa(
                pagopor='TRANSFERÊNCIA',
                descricao=motivo,
                valor=valor_transferido,
                tipo='Entrada',
                carteira_id=conta_destino,
                catcaixa_id=2,
                fornecedor_id=0,
                data_criado=datetime.now(timezone.utc).astimezone(),
            )
        db.session.add(novo_caixa_saida)
        db.session.add(novo_caixa_entrada)
        db.session.commit()
        flash('Valor Transferido!', 'cor-ok')
        return redirect(url_for("Carteiras"))

    return render_template(
        "Caixa/trasferir.html",
        carteiras=carteiras,
        lista_de_valores=lista_de_valores,
    )


@app.route("/Carteiras")
@login_required
@nome_required
@verificacao_nivel(4)
def Carteiras():
    page = request.args.get("page", 1, type=int)
    carteira = Carteirabanco.query.order_by(Carteirabanco.id.desc()).paginate(
        page=page, per_page=10
    )
    page = request.args.get("page", 1, type=int)
    getCaixas = Caixa.query.all()
    get_carteiras = Carteirabanco.query.all()
    lista_de_valores = []
    for cart in get_carteiras:
        carteira_id_saida = []
        caixa_id_entrada = []
        for cartera_caixas in getCaixas:
            valor_calculado = Calculos_gloabal.valor_para_Calculos(cartera_caixas.valor)
            if cart.id == cartera_caixas.carteira_id:
                if cartera_caixas.tipo == "Saida":
                    carteira_id_saida.append(valor_calculado)
                else:
                    caixa_id_entrada.append(valor_calculado)
        somar_entrada = sum(caixa_id_entrada)
        somar_saida = sum(carteira_id_saida)
        somas_total = somar_entrada - somar_saida
        somas_total = Calculos_gloabal.format_valor_moeda(somas_total)
        lista_de_valores.append(
            {
                "id": cart.id,
                "nome": cart.nome,
                "valor": somas_total,
            }
        )
        total_caixa = Caixa.Saldo_Caixa()
    return render_template(
        "/umDado.html",
        lista_de_valores=lista_de_valores,
        perfils=carteira,
        perfil="Carteiras",
        produto="Carteiras",
        total_caixa=total_caixa,
    )


@app.route("/addCarteiras", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addCarteiras():
    return Redutor_codigo.handle_generic_add(
        request, Carteirabanco, "nome", "Carteiras"
    )


@app.route("/atulizCarteiras/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def atulizCarteiras(id):
    return Redutor_codigo.handle_generic_update(
        request, Carteirabanco, id, "nome", "Carteiras"
    )


@app.route("/deleteCarteiras/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteCarteiras(id):
    return Redutor_codigo.handle_generic_delete(
        request, Carteirabanco, id, "nome", "Carteiras"
    )


@app.route("/searchCarteiras", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def searchcarteiras():
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = f"%{search_value}%"
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            getCaixas = Caixa.query.all()
            get_carteiras = (
                Carteirabanco.query.filter(getattr(Carteirabanco, escolha).like(search))
                .order_by(Carteirabanco.id.desc())
                .paginate(page=page, per_page=10)
            )
            lista_de_valores = []
            for cart in get_carteiras:
                carteira_id_saida = []
                caixa_id_entrada = []
                for cartera_caixas in getCaixas:
                    valor_calculado = Calculos_gloabal.valor_para_Calculos(cartera_caixas.valor)
                    if cart.id == cartera_caixas.carteira_id:
                        if cartera_caixas.tipo == "Saida":
                            carteira_id_saida.append(valor_calculado)
                        else:
                            caixa_id_entrada.append(valor_calculado)
                somar_entrada = sum(caixa_id_entrada)
                somar_saida = sum(carteira_id_saida)
                somas_total = somar_entrada - somar_saida
                somas_total = Calculos_gloabal.format_valor_moeda(somas_total)
                lista_de_valores.append(
                    {
                        "id": cart.id,
                        "nome": cart.nome,
                        "valor": somas_total,
                    }
                )
                total_caixa = Caixa.Saldo_Caixa()
            return render_template(
                "/umDado.html",
                busca=busca,
                escolha=escolha,
                lista_de_valores=lista_de_valores,
                perfils=get_carteiras,
                perfil="Carteiras",
                produto="Carteiras",
                total_caixa=total_caixa,
            )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


# Caixa
@app.route("/Caixas/<string:tipo>")
@login_required
@nome_required
@verificacao_nivel(4)
def Caixas(tipo):
    if tipo == "Todos":
        page = request.args.get("page", 1, type=int)
        getCaixa = (
            Caixa.query.filter(Caixa.id)
            .order_by(Caixa.data_criado.desc())
            .paginate(page=page, per_page=10)
        )
    else:
        page = request.args.get("page", 1, type=int)
        getCaixa = (
            Caixa.query.filter(Caixa.tipo == tipo)
            .order_by(Caixa.data_criado.desc())
            .paginate(page=page, per_page=10)
        )
    total_caixa = Caixa.Saldo_Caixa()
    return render_template(
        "Caixa/Caixa.html",
        Caixas=getCaixa,
        tipo=tipo,
        total_caixa=total_caixa,
    )


@app.route("/addCaixas/<string:tipo>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addCaixas(tipo):
    form = AddCaixas()
    carteiras = Carteirabanco.query.all()
    carteira_choices = [("", "Selecione uma carteira")] + [
        (carteira.id, carteira.nome) for carteira in carteiras
    ]
    form.carteira_id.choices = carteira_choices
    catcaixas = Catcaixa.query.filter(~Catcaixa.id.in_([1, 2])).all()
    catcaixa_choices = [("", "Selecione uma categoria")] + [
        (catcaixa.id, catcaixa.nome) for catcaixa in catcaixas
    ]

    form.catcaixa_id.choices = catcaixa_choices
    fornecedores = Fornecedor.query.all()
    fornecedor_choices = [(0, "Selecione um fornecedor")] + [
        (fornecedor.id, fornecedor.nome) for fornecedor in fornecedores
    ]
    form.fornecedor_id.choices = fornecedor_choices
    if form.validate_on_submit():
        filtro_Fornecedor = form.fornecedor_id.data
        if filtro_Fornecedor == "0" and tipo != "Entrada":
            flash("Informe o Fornecedor", "cor-alerta")
        else:
            novo_caixa = Caixa(
                pagopor=form.pagopor.data.upper(),
                descricao=form.descricao.data.upper(),
                valor=form.valor.data,
                tipo=tipo,
                carteira_id=form.carteira_id.data,
                catcaixa_id=form.catcaixa_id.data,
                fornecedor_id=form.fornecedor_id.data,
                data_criado=datetime.now(timezone.utc).astimezone(),
            )
            db.session.add(novo_caixa)
            db.session.commit()
            return redirect(url_for("Caixas", tipo=tipo))
    return render_template(
        "/Caixa/addCaixa.html",
        form=form,
        tipo=tipo,
    )


@app.route("/atulizCaixas/<int:id>/<string:tipo>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def atulizCaixas(id, tipo):
    try:
        getCaixa = Caixa.query.get_or_404(id)
        if getCaixa.catcaixa_id == 1 or getCaixa.catcaixa_id == 2:
            flash(f"Evite usar a barra de navegação para isso.!!!", "cor-cancelar")
            return redirect(url_for("Caixas", tipo=tipo))
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
        filtro = Caixa.query.filter(
            (getCaixa.data_criado > data_hora_especifica)
        ).first()
        if filtro:
            form = AddCaixas(request.form)
            if request.method == "POST":
                carteiras = Carteirabanco.query.all()
                form.carteira_id.choices = [
                    (carteira.id, carteira.nome) for carteira in carteiras
                ]
                catcaixas = Catcaixa.query.all()
                form.catcaixa_id.choices = [
                    (catcaixa.id, catcaixa.nome) for catcaixa in catcaixas
                ]
                fornecedores = Fornecedor.query.all()
                form.fornecedor_id.choices = [
                    (fornecedor.id, fornecedor.nome) for fornecedor in fornecedores
                ]
                if tipo == "Entrada":
                    form.fornecedor_id.data = 0
                attributes = [
                    "pagopor",
                    "descricao",
                    "valor",
                ]
                attributesUpper = [
                    "carteira_id",
                    "catcaixa_id",
                    "fornecedor_id",
                ]

                for attribute in attributes:
                    setattr(
                        getCaixa,
                        attribute,
                        getattr(form, attribute).data.upper().strip(),
                    )
                for attributeUpper in attributesUpper:
                    setattr(
                        getCaixa,
                        attributeUpper,
                        getattr(form, attributeUpper).data,
                    )

                db.session.commit()
                flash(f"A Caixa, Foi Atulizado com Sucesso!!!", "cor-ok")
                return redirect(url_for("Caixas", tipo=tipo))
            attributes = [
                "pagopor",
                "descricao",
                "valor",
            ]

            for attribute in attributes:
                getattr(form, attribute).data = getattr(getCaixa, attribute)
            carteiras = Carteirabanco.query.all()
            carteira_choices = [(getCaixa.carteira.id, getCaixa.carteira.nome)] + [
                (carteira.id, carteira.nome) for carteira in carteiras
            ]
            form.carteira_id.choices = carteira_choices
            catcaixas = Catcaixa.query.filter((~Catcaixa.id.in_([1, 2]))).all()
            catcaixa_choices = [(getCaixa.catcaixa.id, getCaixa.catcaixa.nome)] + [
                (catcaixa.id, catcaixa.nome) for catcaixa in catcaixas
            ]
            form.catcaixa_id.choices = catcaixa_choices
            fornecedores = Fornecedor.query.all()
            if getCaixa.tipo == "Entrada":
                fornecedor_choices = [(0, 0)] + [
                    (fornecedor.id, fornecedor.nome) for fornecedor in fornecedores
                ]
                form.fornecedor_id.choices = fornecedor_choices
            else:
                fornecedor_choices = [
                    (getCaixa.fornecedor.id, getCaixa.fornecedor.nome)
                ] + [(fornecedor.id, fornecedor.nome) for fornecedor in fornecedores]
                form.fornecedor_id.choices = fornecedor_choices
            return render_template(
                "/Caixa/addCaixa.html",
                produto="Caixa",
                atulizar="atulizar",
                form=form,
                Caixa=getCaixa,
                tipo=tipo,
            )
        else:
            flash(
                f"A {getCaixa.tipo} dos meses passados, não podem ser Atulizadas!",
                "cor-cancelar",
            )
            return redirect(url_for("Caixas", tipo=tipo))
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deleteCaixas/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteCaixas(id):
    try:
        getCaixa = Caixa.query.get_or_404(id)
        if getCaixa.catcaixa_id == 1 or getCaixa.catcaixa_id == 2:
            flash(f"Evite usar a barra de navegação para isso.!!!", "cor-cancelar")
            return redirect(url_for("Caixas", tipo='Todos'))
        if request.method == "POST":
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
                filtro = Caixa.query.filter(
                    (getCaixa.data_criado > data_hora_especifica)
                ).first()
                if filtro:
                    db.session.delete(getCaixa)
                    db.session.commit()
                    flash(
                        f"A {getCaixa.tipo} foi Deletada com Sucesso!!!",
                        "cor-ok",
                    )
                else:
                    flash(
                        f"A {getCaixa.tipo} não foi APAGADA, {getCaixa.tipo} dos meses anteriores não podem ser apagadas!",
                        "cor-cancelar",
                    )
                return jsonify()
            except:
                flash(
                    f"A {getCaixa.tipo} Não pode ser APAGADO!",
                    "cor-alerta",
                )
                return jsonify()
        flash(f"A Caixa NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchCaixas/<string:tipo>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def searchCaixas(tipo):
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "categoria":
                if tipo == "Todos":
                    getCaixa = (
                        Caixa.query.filter(
                            Caixa.catcaixa.has(Catcaixa.nome.like(search))
                        )
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    getCaixa = (
                        Caixa.query.filter(
                            and_(
                                Caixa.tipo == tipo,
                                Caixa.catcaixa.has(Catcaixa.nome.like(search)),
                            )
                        )
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
            elif escolha == "fornecedor":
                if tipo == "Todos":
                    getCaixa = (
                        Caixa.query.filter(
                            Caixa.fornecedor.has(Fornecedor.nome.like(search))
                        )
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    getCaixa = (
                        Caixa.query.filter(
                            and_(
                                Caixa.tipo == tipo,
                                Caixa.fornecedor.has(Fornecedor.nome.like(search)),
                            )
                        )
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
            elif escolha == "carteira":
                if tipo == "Todos":
                    getCaixa = (
                        Caixa.query.filter(
                            Caixa.carteira.has(Carteirabanco.nome.like(search))
                        )
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    getCaixa = (
                        Caixa.query.filter(
                            and_(
                                Caixa.tipo == tipo,
                                Caixa.carteira.has(Carteirabanco.nome.like(search)),
                            )
                        )
                        .order_by(Caixa.data_criado.desc())
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
                        if tipo == "Todos":
                            query = Caixa.query.filter(
                                Caixa.data_criado > data_hora_especifica,
                            ).order_by(Caixa.data_criado.desc())
                        else:
                            query = Caixa.query.filter(
                                Caixa.data_criado > data_hora_especifica,
                                Caixa.tipo == tipo,
                            ).order_by(Caixa.data_criado.desc())
                        getCaixa = query.paginate(page=page, per_page=10)
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
                        if tipo == "Todos":
                            query = Caixa.query.filter(
                                Caixa.data_criado.between(data_inicial, data_final),
                            ).order_by(Caixa.data_criado.desc())
                        else:
                            query = Caixa.query.filter(
                                Caixa.data_criado.between(data_inicial, data_final),
                                Caixa.tipo == tipo,
                            ).order_by(Caixa.data_criado.desc())
                        getCaixa = query.paginate(page=page, per_page=10)
                    else:
                        flash(
                            "Algo deu errado!!!! Confira a data digitada", "cor-alerta"
                        )
                        return redirect(url_for("Caixas", tipo=tipo))
                except:
                    flash("Algo deu errado!!!! Confira a data digitada", "cor-alerta")
                    return redirect(url_for("Caixas", tipo=tipo))
            elif escolha == "todos":
                if tipo == "Todos":
                    search_terms = search.split()  
                    conditions = []

                    for term in search_terms:
                        conditions.append(
                            or_(
                                Caixa.id.like(f'%{term}%'),
                                Caixa.pagopor.like(f'%{term}%'),
                                Caixa.descricao.like(f'%{term}%'),
                                Caixa.valor.like(f'%{term}%'),
                                Caixa.data_criado.like(f'%{term}%'),
                                Caixa.tipo.like(f'%{term}%'),
                                Caixa.carteira.has(Carteirabanco.nome.like(f'%{term}%')),
                                Caixa.catcaixa.has(Catcaixa.nome.like(f'%{term}%')),
                                Caixa.fornecedor.has(Fornecedor.nome.like(f'%{term}%')),
                            )
                        )

                    getCaixa = (
                        Caixa.query.filter(
                            *conditions
                        )
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )

                else:
                    search_terms = search.split()  
                    conditions = []
                    for term in search_terms:
                        conditions.append(
                            or_(
                                Caixa.id.like(f'%{term}%'),
                                Caixa.pagopor.like(f'%{term}%'),
                                Caixa.descricao.like(f'%{term}%'),
                                Caixa.valor.like(f'%{term}%'),
                                Caixa.data_criado.like(f'%{term}%'),
                                Caixa.carteira.has(Carteirabanco.nome.like(f'%{term}%')),
                                Caixa.catcaixa.has(Catcaixa.nome.like(f'%{term}%')),
                                Caixa.fornecedor.has(Fornecedor.nome.like(f'%{term}%')),
                            )
                        )

                    getCaixa = (
                        Caixa.query.filter(
                            *conditions,
                            Caixa.tipo == tipo,
                        )
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
            else:
                if tipo == "Todos":
                    getCaixa = (
                        Caixa.query.filter(getattr(Caixa, escolha).like(search))
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
                else:
                    getCaixa = (
                        Caixa.query.filter(getattr(Caixa, escolha).like(search))
                        .filter(Caixa.tipo == tipo)
                        .order_by(Caixa.data_criado.desc())
                        .paginate(page=page, per_page=10)
                    )
            total_caixa = Caixa.Saldo_Caixa()
            return render_template(
                "Caixa/Caixa.html",
                Caixas=getCaixa,
                busca=busca,
                escolha=escolha,
                tipo=tipo,
                total_caixa=total_caixa,
            )
        else:
            return redirect(url_for("Caixas", tipo=tipo))
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/GraficoMesTotal", methods=["GET", "POST"])
def GraficoMesTotal():
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
    buscarGanhos = Caixa.query.filter(
        (Caixa.data_criado > data_hora_especifica)
    ).first()

    return jsonify()
