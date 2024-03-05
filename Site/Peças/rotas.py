from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    request,
    current_app,
    jsonify,
)
from .formolarios import Addpeças
from Site import db, app, photos, nome_required, verificacao_nivel
from Site.Global.fun_global import Calculos_gloabal, Redutor_codigo, Edit_global
from .modelos import Marcapeça, Peça
import secrets
import os
from Site.Fornecedor.modelos import Fornecedor
from Site.Carros.modelos import Carro
from flask_login import login_required
import random
import string
from faker import Faker 
from sqlalchemy import or_

@app.route("/lopPeças/<int:numero>")
@login_required
@nome_required
@verificacao_nivel(3)
def lopPeças(numero):
    fake = Faker('pt_BR')
    def gerar_codigo_ficticio():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=11))
    for _ in range(numero):
        cadastrar = Marcapeça(
            nome=fake.name().upper(),
        )

        db.session.add(cadastrar)
    db.session.commit()

    lista_marcas = Marcapeça.query.all()

    if not lista_marcas:
        return "Lista de marcas vazia."

    for peça in lista_marcas:
        codigo_barra = random.randint(0, 1000000000000)
        
        valor_pago_int = random.randint(0, 1000)
        valor_pago = Calculos_gloabal.format_valor_moeda(valor_pago_int)
        valor_venda_int = valor_pago_int * 2
        valor_venda = Calculos_gloabal.format_valor_moeda(valor_venda_int)

        estoque = random.randint(0, 100)

        criar = Peça(
            nome=fake.sentence(nb_words=2, variable_nb_words=True).upper(),
            codigo=gerar_codigo_ficticio().upper(), 
            codigo_debarra=codigo_barra,
            pago=valor_pago,
            preso=valor_venda,
            estoque=estoque,
            carro=[],
            descrisao=fake.sentence(),
            marca_id=peça.id,
            fornecedor_id=1,
            image_1="foto.jpg",
            image_2="foto.jpg",
            image_3="foto.jpg",
        )

        db.session.add(criar)

    db.session.commit()

    return redirect("/Peças")


@app.route("/Marca_das_Peças")
@login_required
@nome_required
@verificacao_nivel(3)
def Marca_das_Peças():
    try:
        page = request.args.get("page", 1, type=int)
        marcaPesa = Marcapeça.query.order_by(Marcapeça.id.desc()).paginate(
            page=page, per_page=10
        )
        return render_template(
            "/umDado.html",
            perfils=marcaPesa,
            perfil="Marca_das_Peças",
            produto="Marca das Peças",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addMarca_das_Peças", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addMarca_das_Peças():
    return Redutor_codigo.handle_generic_add(
        request, Marcapeça, "nome", "Marca_das_Peças"
    )


@app.route("/atulizMarca_das_Peças/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizMarca_das_Peças(id):
    return Redutor_codigo.handle_generic_update(
        request, Marcapeça, id, "nome", "Marca_das_Peças"
    )


@app.route("/deleteMarca_das_Peças/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteMarca_das_Peças(id):
    return Redutor_codigo.handle_generic_delete(
        request, Marcapeça, id, "nome", "Marca_das_Peças"
    )


@app.route("/searchMarca_das_Peças", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchMarca_das_Peças():
    return Redutor_codigo.search_generic(Marcapeça, "Marca_das_Peças")


# Peças


@app.route("/Peças")
@login_required
@nome_required
@verificacao_nivel(3)
def Peças():
    try:
        page = request.args.get("page", 1, type=int)
        getPeça = Peça.query.order_by(Peça.id).paginate(page=page, per_page=10)
        CatPeça = Marcapeça.query.all()
        fornecedors = Fornecedor.query.all()
        return render_template(
            "Peças/Peça.html",
            Peças=getPeça,
            marcas=CatPeça,
            fornecedors=fornecedors,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addPeças", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addPeças():
    try:
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        marcasPro = Marcapeça.query.all()
        fornecedors = Fornecedor.query.all()
        form = Addpeças()
        if form.validate_on_submit():
            carro = request.form.getlist("carros")
            marcaPro = request.form.get("marcaPro")
            fornecedor = request.form.get("fornecedor")
            filtro = Peça.query.filter_by(codigo=form.codigo.data.strip()).first()
            if filtro:
                flash(
                    f"O Codigo {filtro.codigo} Jã esta cadastrado!!!",
                    "cor-alerta",
                )
            else:
                try:
                    image_1 = photos.save(
                        request.files.get("image_1"), name=secrets.token_hex(10) + "..."
                    )
                except:
                    image_1 = "foto.jpg"
                try:
                    image_2 = photos.save(
                        request.files.get("image_2"), name=secrets.token_hex(10) + "..."
                    )
                except:
                    image_2 = "foto.jpg"
                try:
                    image_3 = photos.save(
                        request.files.get("image_3"), name=secrets.token_hex(10) + "..."
                    )
                except:
                    image_3 = "foto.jpg"
                addpro = Peça(
                    nome=form.nome.data.upper().strip(),
                    codigo=form.codigo.data.strip(),
                    codigo_debarra=form.codigo_debarra.data.strip(),
                    pago=form.pago.data.strip(),
                    preso=form.preso.data.strip(),
                    estoque=form.estoque.data.strip(),
                    carro=carro,
                    descrisao=form.descrisao.data.upper().strip(),
                    marca_id=marcaPro,
                    fornecedor_id=fornecedor,
                    image_1=image_1,
                    image_2=image_2,
                    image_3=image_3,
                )
                db.session.add(addpro)
                db.session.commit()
                return redirect(url_for("Peças"))
        return render_template(
            "/Peças/addpeça.html",
            form=form,
            produto="Peça",
            marcasPro=marcasPro,
            marcas=marcas,
            fornecedors=fornecedors,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizPeças/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizPeças(id):
    try:
        getPeça = Peça.query.get_or_404(id)
        form = Addpeças(request.form)
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        marcasPro = Marcapeça.query.all()
        fornecedors = Fornecedor.query.all()
        carro = request.form.getlist("carros")
        marcaPro = request.form.get("marcaPro")
        fornecedor = request.form.get("fornecedor")
        if request.method == "POST":
            filtro = Peça.query.filter_by(codigo=form.codigo.data.strip()).first()
            if filtro and filtro.codigo != "" and filtro.id != getPeça.id:
                flash(
                    f"O Codigo {filtro.codigo} Jã esta cadastrado!!!",
                    "cor-alerta",
                )
            else:
                if request.files.get("image_1"):
                    if getPeça.image_1 != "foto.jpg":
                        try:
                            os.unlink(
                                os.path.join(
                                    current_app.root_path,
                                    "static/imagens/" + getPeça.image_1,
                                )
                            )
                            getPeça.image_1 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeça.image_1 = "foto.jpg"
                    else:
                        try:
                            getPeça.image_1 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeça.image_1 = "foto.jpg"
                if request.files.get("image_2"):
                    if getPeça.image_2 != "foto.jpg":
                        try:
                            os.unlink(
                                os.path.join(
                                    current_app.root_path,
                                    "static/imagens/" + getPeça.image_2,
                                )
                            )
                            getPeça.image_2 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeça.image_2 = "foto.jpg"
                    else:
                        try:
                            getPeça.image_2 = photos.save(
                                request.files.get("image_2"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeça.image_2 = "foto.jpg"
                if request.files.get("image_3"):
                    if getPeça.image_3 != "foto.jpg":
                        try:
                            os.unlink(
                                os.path.join(
                                    current_app.root_path,
                                    "static/imagens/" + getPeça.image_3,
                                )
                            )
                            getPeça.image_3 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeça.image_3 = "foto.jpg"
                    else:
                        try:
                            getPeça.image_3 = photos.save(
                                request.files.get("image_3"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeça.image_3 = "foto.jpg"

                attributes = [
                    "nome",
                    "codigo",
                    "codigo_debarra",
                    "estoque",
                    "descrisao",
                    "pago",
                    "preso",
                ]

                for attribute in attributes:
                    setattr(
                        getPeça,
                        attribute,
                        getattr(form, attribute).data.upper().strip(),
                    )

                getPeça.fornecedor_id = fornecedor
                getPeça.marca_id = marcaPro
                getPeça.carro = carro

                db.session.commit()
                flash(f"A Peça, Foi Atulizado com Sucesso!!!", "cor-ok")
                return redirect("/Peças")
        attributes = [
            "nome",
            "codigo",
            "codigo_debarra",
            "pago",
            "preso",
            "estoque",
            "descrisao",
        ]

        for attribute in attributes:
            getattr(form, attribute).data = getattr(getPeça, attribute)

        return render_template(
            "/Peças/addpeça.html",
            produto="Peça",
            atulizar="atulizar",
            form=form,
            marcasPro=marcasPro,
            marcas=marcas,
            fornecedors=fornecedors,
            Peça=getPeça,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deletePeças/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deletePeças(id):
    try:
        getPeça = Peça.query.get_or_404(id)
        if request.method == "POST":
            try:
                db.session.delete(getPeça)
                db.session.commit()
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


@app.route("/searchPeças", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchPeças():
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "marca":
                getPeça = Peça.query.filter(
                    Peça.marca.has(Marcapeça.nome.like(search))
                ).paginate(page=page, per_page=4)
            elif escolha == "fornecedor":
                getPeça = Peça.query.filter(
                    Peça.fornecedor.has(Fornecedor.nome.like(search))
                ).paginate(page=page, per_page=4)
            elif escolha == "todos":
                search_terms = search.split()  
                conditions = []
                for term in search_terms:
                    conditions.append(
                        or_(
                            Peça.id.like(f'%{term}%'),
                            Peça.codigo.like(f'%{term}%'),
                            Peça.codigo_debarra.like(f'%{term}%'),
                            Peça.nome.like(f'%{term}%'),
                            Peça.pago.like(f'%{term}%'),
                            Peça.preso.like(f'%{term}%'),
                            Peça.estoque.like(f'%{term}%'),
                            Peça.carro.like(f'%{term}%'),
                            Peça.descrisao.like(f'%{term}%'),
                            Peça.data_criado.like(f'%{term}%'),
                            Peça.marca.has(Marcapeça.nome.like(f'%{term}%')),
                            Peça.fornecedor.has(Fornecedor.nome.like(f'%{term}%')),
                        )
                    )
                getPeça = (
                    Peça.query.filter(
                        *conditions
                    )
                    .order_by(Peça.id.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                getPeça = (
                    Peça.query.filter(getattr(Peça, escolha).like(search))
                    .order_by(Peça.id.desc())
                    .paginate(page=page, per_page=10)
                )
            marcaPesa = Marcapeça.query.all()
            return render_template(
                "Peças/Peça.html",
                Peças=getPeça,
                busca=busca,
                escolha=escolha,
                CatPeça=marcaPesa,
            )
        else:
            return redirect("Peças")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
