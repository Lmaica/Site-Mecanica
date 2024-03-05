from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    request,
    current_app,
    jsonify,
)
from Site import app, db, photos, nome_required, verificacao_nivel
from Site.Global.fun_global import Redutor_codigo
from .modelos import Fornecedor, Catfornecedor
from .formularios import ForFornecedor
import secrets
import os
from flask_login import login_required
import random
from faker import Faker
from sqlalchemy import or_

@app.route("/lopFornecedor/<int:numero>")
@login_required
@nome_required
@verificacao_nivel(3)
def lopFornecedor(numero):
    fake = Faker('pt_BR')

    def criar_fornecedores(lista_categorias, numero):
        if not lista_categorias:
            return None

        for _ in range(numero):
            categoria = random.choice(lista_categorias)

            cadastrar = Fornecedor(
                nome=fake.name().upper(),
                catfornecedor_id=categoria.id,
                fone=f"({fake.random_int(10, 99)}) {fake.random_int(90000, 99999)}-{fake.random_int(1000, 9999)}",
                fone1=f"({fake.random_int(10, 99)}) {fake.random_int(90000, 99999)}-{fake.random_int(1000, 9999)}",
                email=fake.email(),
                cnpj=fake.cpf(),
                cep=fake.postcode(),
                estado=fake.state_abbr(),
                cidade=fake.city(),
                bairro=fake.word().upper(),
                rua=fake.street_name().upper(),
                nuCasa=fake.building_number(),
                complemento=fake.word().upper(),
                obs=fake.name().upper(),
                foto="foto.jpg",
            )

            db.session.add(cadastrar)

        db.session.commit()
        return f"{numero} fornecedores criados com sucesso."

    lista_categorias = Catfornecedor.query.all()
    resultado = criar_fornecedores(lista_categorias, numero)
    
    if resultado:
        flash(resultado)
    else:
        flash("Não há categorias de fornecedores disponíveis.")

    return redirect("/Fornecedors")



@app.route("/Cateforia_do_Fornecedor")
@login_required
@nome_required
@verificacao_nivel(3)
def Cateforia_do_Fornecedor():
    try:
        page = request.args.get("page", 1, type=int)
        CatFornecedor = Catfornecedor.query.order_by(Catfornecedor.id.desc()).paginate(
            page=page, per_page=10
        )
        return render_template(
            "/umDado.html",
            perfils=CatFornecedor,
            perfil="Cateforia_do_Fornecedor",
            produto="Categoria de Fornecedor",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addCateforia_do_Fornecedor", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addCateforia_do_Fornecedor():
    return Redutor_codigo.handle_generic_add(
        request, Catfornecedor, "nome", "Cateforia_do_Fornecedor"
    )


@app.route("/atulizCateforia_do_Fornecedor/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizCateforia_do_Fornecedor(id):
    return Redutor_codigo.handle_generic_update(
        request, Catfornecedor, id, "nome", "Cateforia_do_Fornecedor"
    )


@app.route("/deleteCateforia_do_Fornecedor/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteCateforia_do_Fornecedor(id):
    return Redutor_codigo.handle_generic_delete(
        request, Catfornecedor, id, "nome", "Cateforia_do_Fornecedor"
    )


@app.route("/searchCateforia_do_Fornecedor", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchCateforia_do_Fornecedor():
    return Redutor_codigo.search_generic(Catfornecedor, "Cateforia_do_Fornecedor")


# Adicionar Fornecedor
@app.route("/Fornecedors")
@login_required
@nome_required
@verificacao_nivel(3)
def Fornecedors():
    try:
        page = request.args.get("page", 1, type=int)
        getFornecedor = Fornecedor.query.order_by(Fornecedor.id.desc()).paginate(
            page=page, per_page=10
        )
        CatFornecedor = Catfornecedor.query.all()
        return render_template(
            "Fornecedor/Fornecedor.html",
            Fornecedors=getFornecedor,
            CatFornecedor=CatFornecedor,

        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

@app.route("/addFornecedors", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addFornecedors():
    try:
        form = ForFornecedor()
        categorias = Catfornecedor.query.all()
        if form.validate_on_submit():
            campos_verificacao = [
                ("email", "O Email {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("cnpj", "O CNPJ {} Pertence ao Usuario ID {} Razão Social {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
            ]

            condicao_encontrada = True
            for campo, mensagem in campos_verificacao:
                valor_campo = getattr(form, campo).data
                condicao_encontrada = Redutor_codigo.verificar_existencia(
                    Fornecedor, campo, valor_campo, "0", mensagem
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
                cadastrar = Fornecedor(
                    nome=form.nome.data.upper().strip(),
                    catfornecedor_id=form.catfornecedor.data,
                    fone=form.fone.data.strip(),
                    fone1=form.fone1.data.strip(),
                    email=form.email.data.strip(),
                    cnpj=form.cnpj.data.strip(),
                    cep=form.cep.data.strip(),
                    estado=form.estado.data.upper().strip(),
                    cidade=form.cidade.data.upper().strip(),
                    bairro=form.bairro.data.upper().strip(),
                    rua=form.rua.data.upper().strip(),
                    nuCasa=form.nuCasa.data.strip().replace(" ", ""),
                    complemento=form.complemento.data.upper().strip(),
                    obs=form.obs.data.strip(),
                    foto=foto,
                )
                db.session.add(cadastrar)
                db.session.commit()
                return redirect(url_for("Fornecedors"))
        return render_template(
            "/Fornecedor/addFornecedor.html",
            form=form,
            categorias=categorias,
            produto="Fornecedor",
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizFornecedors/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizFornecedors(id):
    try:
        getFornecedor = Fornecedor.query.get_or_404(id)
        form = ForFornecedor(request.form)
        if form.validate_on_submit():
            campos_verificacao = [
                ("email", "O Email {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("cnpj", "O CNPJ {} Pertence ao Usuario ID {} Razão Social {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
            ]

            condicao_encontrada = True
            for campo, mensagem in campos_verificacao:
                valor_campo = getattr(form, campo).data
                condicao_encontrada = Redutor_codigo.verificar_existencia(
                    Fornecedor, campo, valor_campo, getFornecedor.id, mensagem
                )
                if not condicao_encontrada:
                    break
            if condicao_encontrada:
                if request.files.get("image_1"):
                    if getFornecedor.foto != "foto.jpg":
                        try:
                            os.unlink(
                                os.path.join(
                                    current_app.root_path,
                                    "static/imagens/" + getFornecedor.foto,
                                )
                            )
                        except:
                            getFornecedor.foto = "foto.jpg"
                    else:
                        try:
                            getFornecedor.foto = photos.save(
                                request.files.get("image_1"),
                                name=secrets.token_hex(10) + "...",
                            )
                        except:
                            getFornecedor.foto = "foto.jpg"
                getFornecedor.email = form.email.data.strip()
                getFornecedor.catfornecedor_id = form.catfornecedor.data
                attributes = [
                    "nome",
                    "fone",
                    "cnpj",
                    "cep",
                    "estado",
                    "cidade",
                    "bairro",
                    "rua",
                    "nuCasa",
                    "obs",
                    "complemento",
                ]

                for attribute in attributes:
                    setattr(
                        getFornecedor,
                        attribute,
                        getattr(form, attribute).data.upper().strip(),
                    )
                db.session.commit()
                flash(f"O Fornecedor, Foi Atulizado com Sucesso!!!", "cor-ok")
                return redirect("/Fornecedors")

        attributes = [
            "nome",
            "fone",
            "cnpj",
            "cep",
            "estado",
            "cidade",
            "bairro",
            "rua",
            "nuCasa",
            "complemento",
            "email",
            "obs",
        ]

        for attribute in attributes:
            getattr(form, attribute).data = getattr(getFornecedor, attribute)
        form.catfornecedor.choices.insert(
            0, (getFornecedor.catfornecedor.id, getFornecedor.catfornecedor.nome)
        )
        return render_template(
            "/Fornecedor/addFornecedor.html",
            produto="Fornecedor",
            atulizar="atulizar",
            Fornecedor=getFornecedor,
            form=form,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deleteFornecedors/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteFornecedors(id):
    try:
        getFornecedor = Fornecedor.query.get_or_404(id)
        if request.method == "POST":
            try:
                db.session.delete(getFornecedor)
                db.session.commit()
                flash(
                    f"O Fornecedor do foi Deletada com Sucesso!!!",
                    "cor-ok",
                )
                return jsonify()
            except:
                flash(
                    f"O Fornecedor Não pode ser APAGADO, Ao invés de apagar Modifique, pois a Serviços cadastrados com esse Nome!",
                    "cor-alerta",
                )
                return jsonify()
        flash(f"O Fornecedor NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchFornecedors", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchFornecedors():
    try:
        if request.method == "POST":
            page = request.args.get("page", 1, type=int)
            form = request.form
            search_value = form["search_string"].upper()
            search = "%{0}%".format(search_value)
            escolha = str(request.form.get("searchselector"))
            busca = search_value = form["search_string"]
            if escolha == "categoria":
                getFornecedor = Fornecedor.query.filter(
                    Fornecedor.catfornecedor.has(Catfornecedor.nome.like(search))
                ).paginate(page=page, per_page=10)
            elif escolha == "todos":
                search_terms = search.split()  
                conditions = []
                for term in search_terms:
                    conditions.append(
                        or_(
                            Fornecedor.id.like(f'%{term}%'),
                            Fornecedor.nome.like(f'%{term}%'),
                            Fornecedor.fone.like(f'%{term}%'),
                            Fornecedor.fone1.like(f'%{term}%'),
                            Fornecedor.email.like(f'%{term}%'),
                            Fornecedor.niver.like(f'%{term}%'),
                            Fornecedor.razaoSocial.like(f'%{term}%'),
                            Fornecedor.nomeFantasia.like(f'%{term}%'),
                            Fornecedor.cnpj.like(f'%{term}%'),
                            Fornecedor.cpf.like(f'%{term}%'),
                            Fornecedor.rg.like(f'%{term}%'),
                            Fornecedor.cep.like(f'%{term}%'),
                            Fornecedor.estado.like(f'%{term}%'),
                            Fornecedor.cidade.like(f'%{term}%'),
                            Fornecedor.bairro.like(f'%{term}%'),
                            Fornecedor.rua.like(f'%{term}%'),
                            Fornecedor.nuCasa.like(f'%{term}%'),
                            Fornecedor.complemento.like(f'%{term}%'),
                            Fornecedor.data_criado.like(f'%{term}%'),
                            Fornecedor.catfornecedor.has(Catfornecedor.nome.like(f'%{term}%')),
                        )
                    )

                getFornecedor = (
                    Fornecedor.query.filter(
                        *conditions
                    )
                    .order_by(Fornecedor.id.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                getFornecedor = (
                    Fornecedor.query.filter(getattr(Fornecedor, escolha).like(search))
                    .order_by(Fornecedor.id.desc())
                    .paginate(page=page, per_page=10)
                )
            CatFornecedor = Catfornecedor.query.all()
            return render_template(
                "Fornecedor/Fornecedor.html",
                Fornecedors=getFornecedor,
                busca=busca,
                escolha=escolha,
                CatFornecedor=CatFornecedor,
            )
        else:
            return redirect("Fornecedors")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
