from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    request,
    current_app,
    jsonify,
)
from .formolarios import Addpecas
from Site import db, app, photos, nome_required, verificacao_nivel
from Site.Global.fun_global import Calculos_gloabal, Redutor_codigo, Edit_global
from .modelos import Marcapeca, Peca
import secrets
import os
from Site.Fornecedor.modelos import Fornecedor
from Site.Carros.modelos import Carro
from flask_login import login_required
import random
import string
from faker import Faker 
from sqlalchemy import or_

@app.route("/lopPecas/<int:numero>")
@login_required
@nome_required
@verificacao_nivel(3)
def lopPecas(numero):
    fake = Faker('pt_BR')
    def gerar_codigo_ficticio():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=11))
    for _ in range(numero):
        cadastrar = Marcapeca(
            nome=fake.name().upper(),
        )

        db.session.add(cadastrar)
    db.session.commit()

    lista_marcas = Marcapeca.query.all()

    if not lista_marcas:
        return "Lista de marcas vazia."

    for peca in lista_marcas:
        codigo_barra = random.randint(0, 1000000000000)
        
        valor_pago_int = random.randint(0, 1000)
        valor_pago = Calculos_gloabal.format_valor_moeda(valor_pago_int)
        valor_venda_int = valor_pago_int * 2
        valor_venda = Calculos_gloabal.format_valor_moeda(valor_venda_int)

        estoque = random.randint(0, 100)

        criar = Peca(
            nome=fake.sentence(nb_words=2, variable_nb_words=True).upper(),
            codigo=gerar_codigo_ficticio().upper(), 
            codigo_debarra=codigo_barra,
            pago=valor_pago,
            preso=valor_venda,
            estoque=estoque,
            carro=[],
            descrisao=fake.sentence(),
            marca_id=peca.id,
            fornecedor_id=1,
            image_1="foto.jpg",
            image_2="foto.jpg",
            image_3="foto.jpg",
        )

        db.session.add(criar)

    db.session.commit()

    return redirect("/Pecas")


@app.route("/Marca_das_Pecas")
@login_required
@nome_required
@verificacao_nivel(3)
def Marca_das_Pecas():
    try:
        page = request.args.get("page", 1, type=int)
        marcaPesa = Marcapeca.query.order_by(Marcapeca.id.desc()).paginate(
            page=page, per_page=10
        )
        return render_template(
            "/umDado.html",
            perfils=marcaPesa,
            perfil="Marca_das_Pecas",
            produto="Marca das Pecas",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addMarca_das_Pecas", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addMarca_das_Pecas():
    return Redutor_codigo.handle_generic_add(
        request, Marcapeca, "nome", "Marca_das_Pecas"
    )


@app.route("/atulizMarca_das_Pecas/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizMarca_das_Pecas(id):
    return Redutor_codigo.handle_generic_update(
        request, Marcapeca, id, "nome", "Marca_das_Pecas"
    )


@app.route("/deleteMarca_das_Pecas/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteMarca_das_Pecas(id):
    return Redutor_codigo.handle_generic_delete(
        request, Marcapeca, id, "nome", "Marca_das_Pecas"
    )


@app.route("/searchMarca_das_Pecas", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchMarca_das_Pecas():
    return Redutor_codigo.search_generic(Marcapeca, "Marca_das_Pecas")


# Pecas


@app.route("/Pecas")
@login_required
@nome_required
@verificacao_nivel(3)
def Pecas():
    try:
        page = request.args.get("page", 1, type=int)
        getPeca = Peca.query.order_by(Peca.id).paginate(page=page, per_page=10)
        CatPeca = Marcapeca.query.all()
        fornecedors = Fornecedor.query.all()
        return render_template(
            "Pecas/Peca.html",
            Pecas=getPeca,
            marcas=CatPeca,
            fornecedors=fornecedors,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addPecas", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addPecas():
    try:
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        marcasPro = Marcapeca.query.all()
        fornecedors = Fornecedor.query.all()
        form = Addpecas()
        if form.validate_on_submit():
            carro = request.form.getlist("carros")
            marcaPro = request.form.get("marcaPro")
            fornecedor = request.form.get("fornecedor")
            filtro = Peca.query.filter_by(codigo=form.codigo.data.strip()).first()
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
                addpro = Peca(
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
                return redirect(url_for("Pecas"))
        return render_template(
            "/Pecas/addpeca.html",
            form=form,
            produto="Peca",
            marcasPro=marcasPro,
            marcas=marcas,
            fornecedors=fornecedors,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizPecas/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizPecas(id):
    try:
        getPeca = Peca.query.get_or_404(id)
        form = Addpecas(request.form)
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        marcasPro = Marcapeca.query.all()
        fornecedors = Fornecedor.query.all()
        carro = request.form.getlist("carros")
        marcaPro = request.form.get("marcaPro")
        fornecedor = request.form.get("fornecedor")
        if request.method == "POST":
            filtro = Peca.query.filter_by(codigo=form.codigo.data.strip()).first()
            if filtro and filtro.codigo != "" and filtro.id != getPeca.id:
                flash(
                    f"O Codigo {filtro.codigo} Jã esta cadastrado!!!",
                    "cor-alerta",
                )
            else:
                if request.files.get("image_1"):
                    if getPeca.image_1 != "foto.jpg":
                        try:
                            os.unlink(
                                os.path.join(
                                    current_app.root_path,
                                    "static/imagens/" + getPeca.image_1,
                                )
                            )
                            getPeca.image_1 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeca.image_1 = "foto.jpg"
                    else:
                        try:
                            getPeca.image_1 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeca.image_1 = "foto.jpg"
                if request.files.get("image_2"):
                    if getPeca.image_2 != "foto.jpg":
                        try:
                            os.unlink(
                                os.path.join(
                                    current_app.root_path,
                                    "static/imagens/" + getPeca.image_2,
                                )
                            )
                            getPeca.image_2 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeca.image_2 = "foto.jpg"
                    else:
                        try:
                            getPeca.image_2 = photos.save(
                                request.files.get("image_2"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeca.image_2 = "foto.jpg"
                if request.files.get("image_3"):
                    if getPeca.image_3 != "foto.jpg":
                        try:
                            os.unlink(
                                os.path.join(
                                    current_app.root_path,
                                    "static/imagens/" + getPeca.image_3,
                                )
                            )
                            getPeca.image_3 = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeca.image_3 = "foto.jpg"
                    else:
                        try:
                            getPeca.image_3 = photos.save(
                                request.files.get("image_3"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getPeca.image_3 = "foto.jpg"

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
                        getPeca,
                        attribute,
                        getattr(form, attribute).data.upper().strip(),
                    )

                getPeca.fornecedor_id = fornecedor
                getPeca.marca_id = marcaPro
                getPeca.carro = carro

                db.session.commit()
                flash(f"A Peça, Foi Atulizado com Sucesso!!!", "cor-ok")
                return redirect("/Pecas")
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
            getattr(form, attribute).data = getattr(getPeca, attribute)

        return render_template(
            "/Pecas/addpeca.html",
            produto="Peca",
            atulizar="atulizar",
            form=form,
            marcasPro=marcasPro,
            marcas=marcas,
            fornecedors=fornecedors,
            Peca=getPeca,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deletePecas/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deletePecas(id):
    try:
        getPeca = Peca.query.get_or_404(id)
        if request.method == "POST":
            try:
                db.session.delete(getPeca)
                db.session.commit()
                
                try:
                    if getPeca.image_1 != "foto.jpg":
                        os.remove(
                            os.path.join(
                                current_app.root_path, "static/imagens/" + getPeca.image_1
                            )
                        )
                    else:
                        pass
                except Exception as e:
                    pass
                try:
                    if getPeca.image_1 != "foto.jpg":
                        os.remove(
                            os.path.join(
                                current_app.root_path, "static/imagens/" + getPeca.image_2
                            )
                        )
                    else:
                        pass
                except:
                    pass
                try:
                    if getPeca.image_1 != "foto.jpg":
                        os.remove(
                            os.path.join(
                                current_app.root_path, "static/imagens/" + getPeca.image_3
                            )
                        )
                    else:
                        pass
                except:
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


@app.route("/searchPecas", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchPecas():
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "marca":
                getPeca = Peca.query.filter(
                    Peca.marca.has(Marcapeca.nome.like(search))
                ).paginate(page=page, per_page=4)
            elif escolha == "fornecedor":
                getPeca = Peca.query.filter(
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
                getPeca = (
                    Peca.query.filter(
                        *conditions
                    )
                    .order_by(Peca.id.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                getPeca = (
                    Peca.query.filter(getattr(Peca, escolha).like(search))
                    .order_by(Peca.id.desc())
                    .paginate(page=page, per_page=10)
                )
            marcaPesa = Marcapeca.query.all()
            return render_template(
                "Pecas/Peca.html",
                Pecas=getPeca,
                busca=busca,
                escolha=escolha,
                CatPeca=marcaPesa,
            )
        else:
            return redirect("Pecas")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
