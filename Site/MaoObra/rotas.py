from flask import render_template, session, request, url_for, flash, redirect, jsonify
from Site import app, db, nome_required, verificacao_nivel
from Site.Global.fun_global import Calculos_gloabal, Redutor_codigo, Edit_global
from Site.Carros.modelos import Carro
from .modelos import Maoobra, Catmaoobra, Nomemaoobra, Valorhora
from sqlalchemy import desc
from flask_login import login_required
import random
import string
from faker import Faker
from sqlalchemy import or_

@app.route("/lopMDO/<int:numero>")
@login_required
@nome_required
@verificacao_nivel(3)
def lopMDO(numero):
    fake = Faker('pt_BR')

    for _ in range(numero):
        cadastrar = Nomemaoobra(
            nome=fake.sentence(nb_words=2, variable_nb_words=True).upper(),
        )

        db.session.add(cadastrar)
    db.session.commit()

    def gerar_codigo_ficticio():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=11))
    
    lista_nomemaoobras = Nomemaoobra.query.all()

    if not lista_nomemaoobras:
        return "Lista de nomemaoobras vazia."


    for nomemaoobra in lista_nomemaoobras:
        valor_pago_int = random.randint(0, 1000)
        valor_venda_int = valor_pago_int * 2
        valor_venda = Calculos_gloabal.format_valor_moeda(valor_venda_int)

        
        estoque = random.randint(1, 100)
        categoria = random.randint(0, 2)
        criar = Maoobra(
            nomemaoobra_id=nomemaoobra.id,
            tempo=estoque,
            preso=valor_venda,
            marca='TODOS',
            modelo='TODOS',
            anoIni='TODOS',
            anoFin='TODOS',
            motor='TODOS',
            catmaoobra_id=categoria,
            obs=fake.sentence(),
        )

        db.session.add(criar)

    db.session.commit()

    return redirect("/MaoObras")

@app.route("/MaoObras")
@login_required
@nome_required
@verificacao_nivel(3)
def MaoObras():
    try:
        page = request.args.get("page", 1, type=int)
        MaoObras = Maoobra.query.order_by(Maoobra.id.desc()).paginate(
            page=page, per_page=10
        )
        CatMaoObra = Catmaoobra.query.all()
        NomeMaoObra = Nomemaoobra.query.all()
        return render_template(
            "MaoObras/maoObra.html",
            MaoObras=MaoObras,
            NomeMaoObra=NomeMaoObra,
            CatMaoObra=CatMaoObra,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizMaoObra/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizMaoObra(id):
    try:
        MaoObra = Maoobra.query.get_or_404(id)
        if request.method == "POST":
            hora = request.form.get("hora")
            nomemaoobra = request.form.get("nomemaoobra")
            categoria = request.form.get("categoria")
            preso = request.form.get("preso")
            descrisao = request.form.get("descrisao")
            marca = request.form.get("marcaT") or "TODOS"
            modelo = request.form.get("modeloT") or "TODOS"
            anoIni = request.form.get("anoIniT") or "TODOS"
            anoFin = request.form.get("anoFinT") or "TODOS"
            motor = request.form.get("motorT") or "TODOS"
            filtro = Maoobra.query.filter_by(
                marca=marca,
                modelo=modelo,
                anoIni=anoIni,
                anoFin=anoFin,
                motor=motor,
                nomemaoobra_id=nomemaoobra,
            ).first()
            if filtro and filtro.id != MaoObra.id:
                flash(
                    f"Já a Mão de Obra Cadastrada com o Nome {filtro.catmaoobra.nome}, Com o Carro ({filtro.marca})({filtro.modelo})({filtro.anoIni})({filtro.anoFin})({filtro.motor})  !!!",
                    "cor-alerta",
                )
            else:
                MaoObra.nomemaoobra_id = nomemaoobra
                MaoObra.tempo = hora
                MaoObra.preso = preso.strip()
                MaoObra.marca = marca
                MaoObra.modelo = modelo
                MaoObra.anoIni = anoIni
                MaoObra.anoFin = anoFin
                MaoObra.motor = motor
                MaoObra.catmaoobra_id = categoria
                MaoObra.obs = descrisao.upper().strip()
                db.session.commit()
                flash(f"A Mão de Obra, Foi Atulizada com Sucesso!!!", "cor-ok")
                return redirect(url_for("MaoObras"))
        marca = MaoObra.marca
        modelo = MaoObra.modelo

        anoIni = MaoObra.anoIni
        anoFin = MaoObra.anoFin
        motor = MaoObra.motor
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        modelos = Carro.query.filter_by(marca=marca).distinct(Carro.modelo).all()
        modelos = Edit_global.remove_repetidos([model.modelo for model in modelos])
        anosIni = (
            Carro.query.filter_by(marca=marca, modelo=modelo).distinct(Carro.ano).all()
        )
        anosIni = Edit_global.remove_repetidos([anoIni.ano for anoIni in anosIni])
        anosFin = (
            Carro.query.filter_by(marca=marca, modelo=modelo)
            .filter(Carro.ano >= anoIni)
            .distinct(Carro.ano)
            .all()
        )
        anosFin = Edit_global.remove_repetidos([anoFin.ano for anoFin in anosFin])
        motors = (
            Carro.query.filter_by(marca=marca, modelo=modelo)
            .filter(Carro.ano.between(anoIni, anoFin))
            .distinct(Carro.motor)
            .all()
        )
        motors = Edit_global.remove_repetidos([motor.motor for motor in motors])
        categorias = Catmaoobra.query.all()
        nomemaoobras = Nomemaoobra.query.all()
        return render_template(
            "MaoObras/addMaoObras.html",
            produto="Mão de obra",
            atulizar="atulizar",
            MaoObra=MaoObra,
            marcas=marcas,
            categorias=categorias,
            nomemaoobras=nomemaoobras,
            modelos=modelos,
            anosI=anosIni,
            anosF=anosFin,
            motors=motors,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addMaoObras", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addMaoObras():
    try:
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        preso = request.form.get("preso")
        descrisao = request.form.get("descrisao")
        categorias = Catmaoobra.query.all()
        nomemaoobras = Nomemaoobra.query.all()
        if request.method == "POST":
            hora = request.form.get("hora")
            nomemaoobra = request.form.get("nomemaoobra")
            categoria = request.form.get("categoria")
            marca = request.form.get("marcaT") or "TODOS"
            modelo = request.form.get("modeloT") or "TODOS"
            anoIni = request.form.get("anoIniT") or "TODOS"
            anoFin = request.form.get("anoFinT") or "TODOS"
            motor = request.form.get("motorT") or "TODOS"
            filtro = Maoobra.query.filter_by(
                marca=marca,
                modelo=modelo,
                anoIni=anoIni,
                anoFin=anoFin,
                motor=motor,
                nomemaoobra_id=nomemaoobra,
            ).first()
            if filtro:
                flash(
                    f"Já a Mão de Obra Cadastrada com o Nome {filtro.catmaoobra.nome}, Com o Carro ({filtro.marca})({filtro.modelo})({filtro.anoIni})({filtro.anoFin})({filtro.motor})  !!!",
                    "cor-alerta",
                )
            else:
                addCar = Maoobra(
                    nomemaoobra_id=nomemaoobra,
                    tempo=hora,
                    preso=preso.strip(),
                    marca=marca,
                    modelo=modelo,
                    anoIni=anoIni,
                    anoFin=anoFin,
                    motor=motor,
                    catmaoobra_id=categoria,
                    obs=descrisao.upper().strip(),
                )
                db.session.add(addCar)
                db.session.commit()
                flash(f"A Mão de Obra, Foi cadatrada com Sucesso!!!", "cor-ok")
                return redirect(url_for("MaoObras"))
        return render_template(
            "MaoObras/addMaoObras.html",
            produto="Mão de obra",
            marcas=marcas,
            categorias=categorias,
            nomemaoobras=nomemaoobras,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deleteMaoObras/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteMaoObras(id):
    try:
        MaoObras = Maoobra.query.get_or_404(id)
        if request.method == "POST":
            try:
                db.session.delete(MaoObras)
                db.session.commit()
                flash(
                    f"A Mão de Obra do foi Deletada com Sucesso!!!",
                    "cor-ok",
                )
                return jsonify()
            except:
                flash(
                    f"A Mão de Obra Não pode ser APAGADO, Ao invés de apagar Modifique, pois a Serviços cadastrados com esse Nome!",
                    "cor-alerta",
                )
                return jsonify()
        flash(f"A Mão de Obra NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchMaoObras", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchMaoObras():
    try:
        if request.method == "POST":
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
                MaoObras=MaoObras,
                busca=busca,
                escolha=escolha,
                NomeMaoObra=NomeMaoObra,
                CatMaoObra=CatMaoObra,
            )
        else:
            return redirect("/MaoObras")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/get_modelosServ", methods=["POST"])
def get_modelosServ():
    marca = request.form["marca"]
    modelos = Carro.query.filter_by(marca=marca).distinct(Carro.modelo).all()
    modelo = Edit_global.remove_repetidos([model.modelo for model in modelos])
    return jsonify({"modelo": modelo})


@app.route("/get_anosIni", methods=["POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def get_anosIni():
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    anosIni = (
        Carro.query.filter_by(marca=marca, modelo=modelo)
        .distinct(Carro.ano)
        .order_by(Carro.ano.desc())
        .all()
    )
    anosIni = Edit_global.remove_repetidos([anoIni.ano for anoIni in anosIni])
    return jsonify({"anosIni": anosIni})


@app.route("/get_anosFin", methods=["POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def get_anosFin():
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    anoIni = request.form["anoIni"]
    anosFin = (
        Carro.query.filter_by(marca=marca, modelo=modelo)
        .filter(Carro.ano >= anoIni)
        .distinct(Carro.ano)
        .order_by(Carro.ano.desc())
        .all()
    )
    anosFin = Edit_global.remove_repetidos([anoFin.ano for anoFin in anosFin])
    return jsonify({"anosFin": anosFin})


@app.route("/get_motorsServ", methods=["POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def get_motorsServ():
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    anoIni = request.form["anoIni"]
    anoFin = request.form["anoFin"]
    motors = (
        Carro.query.filter_by(marca=marca, modelo=modelo)
        .filter(Carro.ano.between(anoIni, anoFin))
        .distinct(Carro.motor)
        .all()
    )
    motors = Edit_global.remove_repetidos([motor.motor for motor in motors])
    return jsonify({"motors": motors})


# mandar valor dinamico
@app.route("/valorHora", methods=["POST"])
@login_required
@nome_required
@verificacao_nivel(5)
def valorHora():
    valor_atual = Valorhora.query.order_by(desc(Valorhora.id)).first()
    valor_decimal = Calculos_gloabal.valor_para_Calculos(valor_atual.valor)
    hora = int(request.form["hora"])
    soma = hora * valor_decimal
    soma_formatada = Calculos_gloabal.format_valor_moeda(soma)
    return jsonify({"soma": soma_formatada})


# Categortia da mão de obra


@app.route("/Categorias_de_Mão_de_Obra")
@login_required
@nome_required
@verificacao_nivel(4)
def Categorias_de_Mão_de_Obra():
    try:
        page = request.args.get("page", 1, type=int)
        catMaoObras = Catmaoobra.query.order_by(Catmaoobra.id.desc()).paginate(
            page=page, per_page=10
        )
        return render_template(
            "/umDado.html",
            perfils=catMaoObras,
            perfil="Categorias_de_Mão_de_Obra",
            produto="Categoria de Mão de Obra",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addCategorias_de_Mão_de_Obra", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addCategorias_de_Mão_de_Obra():
    return Redutor_codigo.handle_generic_add(
        request, Catmaoobra, "nome", "Categorias_de_Mão_de_Obra"
    )


@app.route("/atulizCategorias_de_Mão_de_Obra/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def atulizCategorias_de_Mão_de_Obra(id):
    return Redutor_codigo.handle_generic_update(
        request, Catmaoobra, id, "nome", "Categorias_de_Mão_de_Obra"
    )


@app.route("/deleteCategorias_de_Mão_de_Obra/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteCategorias_de_Mão_de_Obra(id):
    return Redutor_codigo.handle_generic_delete(
        request, Catmaoobra, id, "nome", "Categorias_de_Mão_de_Obra"
    )


@app.route("/searchCategorias_de_Mão_de_Obra", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchCategorias_de_Mão_de_Obra():
    return Redutor_codigo.search_generic(Catmaoobra, "Categorias_de_Mão_de_Obra")


# Nome Mão de Obra
@app.route("/Nome_para_Mao_de_Obra")
@login_required
@nome_required
@verificacao_nivel(3)
def Nome_para_Mao_de_Obra():
    try:
        page = request.args.get("page", 1, type=int)

        NomeMaoObras = Nomemaoobra.query.order_by(Nomemaoobra.id.desc()).paginate(
            page=page, per_page=10
        )
        return render_template(
            "/umDado.html",
            perfils=NomeMaoObras,
            perfil="Nome_para_Mao_de_Obra",
            produto="Nome De Mão de Obra",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addNome_para_Mao_de_Obra", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addNome_para_Mao_de_Obra():
    return Redutor_codigo.handle_generic_add(
        request, Nomemaoobra, "nome", "Nome_para_Mao_de_Obra"
    )


@app.route("/atulizNome_para_Mao_de_Obra/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizNome_para_Mao_de_Obra(id):
    return Redutor_codigo.handle_generic_update(
        request, Nomemaoobra, id, "nome", "Nome_para_Mao_de_Obra"
    )


@app.route("/deleteNome_para_Mao_de_Obra/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteNome_para_Mao_de_Obra(id):
    return Redutor_codigo.handle_generic_delete(
        request, Nomemaoobra, id, "nome", "Nome_para_Mao_de_Obra"
    )


@app.route("/searchNome_para_Mao_de_Obra", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchNome_para_Mao_de_Obra():
    return Redutor_codigo.search_generic(Nomemaoobra, "Nome_para_Mao_de_Obra")


# Valor da Mão de Obra
@app.route("/ValorMDO")
@login_required
@nome_required
@verificacao_nivel(4)
def ValorMDO():
    try:
        page = request.args.get("page", 1, type=int)
        ValorMDOs = Valorhora.query.order_by(Valorhora.id.desc()).paginate(
            page=page, per_page=10
        )
        ultimo_dado = Valorhora.query.order_by(desc(Valorhora.id)).first()
        return render_template(
            "/umDado.html",
            ultimo_dado=ultimo_dado,
            perfils=ValorMDOs,
            perfil="ValorMDO",
            produto="Valor da Mão de Obra",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addValorMDO", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def addValorMDO():
    try:
        if request.method == "POST":
            valorMDO = request.form.get("preso").strip()
            filtro = Valorhora.query.order_by(desc(Valorhora.id)).first()
            compara = Calculos_gloabal.valor_para_Calculos(valorMDO)
            if filtro.valor == valorMDO:
                flash(
                    f"Esse ja é o Valor Atual da Mão de Obra!!!",
                    "cor-alerta",
                )
            elif compara == 0.00:
                flash(
                    f"O Valor R$ 0,00, Não é Valido!!!",
                    "cor-alerta",
                )
            else:
                valor_antigo = Calculos_gloabal.valor_para_Calculos(filtro.valor)
                valor_novo = Calculos_gloabal.valor_para_Calculos(valorMDO)
                diferenca_percentual = Calculos_gloabal.calcular_diferenca_percentual(
                    valor_antigo, valor_novo
                )
                percentual = f"{diferenca_percentual:.2f}"
                valorMDO = Valorhora(valor=valorMDO)
                db.session.add(valorMDO)
                flash(
                    f"O Valor Foi Atualizado com Sucesso!!! Dezeja atulizar todos os Serviços A {percentual}%",
                    "confime",
                )
                session["percentual"] = percentual
                db.session.commit()
                return redirect(url_for("ValorMDO"))
        return render_template(
            "/addUmDado.html",
            dado="",
            perfil="ValorMDO",
            produto="Valor da Mão de Obra",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizMDOvalor", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def atulizMDOvalor():
    try:
        percentual = session.get("percentual", None)
        MaoObras = Maoobra.query.all()
        for i in MaoObras:
            percentual = float(percentual)
            MaoObra = Maoobra.query.get_or_404(i.id)
            valor = Calculos_gloabal.valor_para_Calculos(i.preso)
            soma = Calculos_gloabal.calcular_valor_porcentagem(valor, percentual)
            soma_format = Calculos_gloabal.format_valor_moeda(soma)
            MaoObra.preso = soma_format
            flash(
                "Os Valores Foiram Atualizados com Sucesso!!!",
                "cor-ok",
            )
            db.session.commit()
        if percentual is None:
            flash(
                "Não foi posivel atulizar todas as Mão de obra Consulte o Desenvovedor",
                "cor-cancelar",
            )
            return redirect(url_for("ValorMDO"))
        return redirect(url_for("ValorMDO"))
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
