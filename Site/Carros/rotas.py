from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    request,
    jsonify,
)
from Site import app, db, nome_required, verificacao_nivel
from .modelos import Carro
from flask_login import login_required
from sqlalchemy import or_

@app.route("/carros")
@login_required
@nome_required
@verificacao_nivel(3)
def carros():
    try:
        page = request.args.get("page", 1, type=int)
        carros = Carro.query.order_by(Carro.marca.desc()).paginate(
            page=page, per_page=10
        )
        return render_template("Carros/carros.html", carros=carros)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/addCarros", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addCarros():
    try:
        if request.method == "POST":
            getmarca = request.form.get("marca").upper().strip()
            getano = request.form.get("ano").strip()
            getmodelo = request.form.get("modelo").upper().strip()
            getmotor = request.form.get("motor").strip().upper()
            filtro = Carro.query.filter_by(
                marca=getmarca, modelo=getmodelo, ano=getano, motor=getmotor
            ).first()
            if filtro:
                flash(
                    f"O Carro {getmarca}/ {getmodelo}/ {getano}/{getmotor} Já Esta Cadastrado!!!",
                    "cor-cancelar",
                )
            else:
                carro = Carro(
                    marca=getmarca, ano=getano, modelo=getmodelo, motor=getmotor
                )
                db.session.add(carro)
                db.session.commit()
                flash(
                    f"O Carro {getmarca}/{getmodelo}/{getano}/{getmotor} Foi Cadastrado com Sucesso!!!",
                    "cor-ok",
                )
                return redirect(url_for("addCarros"))
        return render_template("Carros/addCarro.html")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizCarros/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizCarros(id):
    try:
        carro = Carro.query.get_or_404(id)
        if request.method == "POST":
            getmarca = request.form.get("marca").upper().strip()
            getano = request.form.get("ano").strip()
            getmodelo = request.form.get("modelo").upper().strip()
            getmotor = request.form.get("motor").strip().upper()
            filtro = Carro.query.filter_by(
                marca=getmarca, modelo=getmodelo, ano=getano, motor=getmotor
            ).first()
            if filtro and filtro.id != carro.id:
                flash(
                    f"O Carro {getmarca}/ {getmodelo}/ {getano}/{getmotor} Já Esta Cadastrado!!!",
                    "cor-alerta",
                )
            else:
                carro.marca = getmarca
                carro.modelo = getmodelo
                carro.ano = getano
                carro.motor = getmotor
                flash("A Categoria foi atualizado", "success")
                db.session.commit()
                flash(
                    f"O Carro foi Atulizado com Sucesso!!!",
                    "cor-ok",
                )
                return redirect("/carros")
        marca = carro.marca
        modelo = carro.modelo
        ano = carro.ano
        motor = carro.motor

        return render_template(
            "/Carros/editarCarro.html",
            marca=marca,
            modelo=modelo,
            ano=ano,
            motor=motor,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deletecarro/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def deletecarro(id):
    try:
        carro = Carro.query.get_or_404(id)
        if request.method == "POST":
            carromodelo = carro.modelo
            try:
                db.session.delete(carro)
                db.session.commit()
                flash(f"O carro do Modelo {carromodelo} foi Deletada", "cor-ok")
                return jsonify()
            except:
                flash(
                    f"O Carro Não pode ser APAGADO, Ao invés de apagar modifique pois a Veiculos cadastrados com esse modelo!",
                    "cor-alerta",
                )
                return jsonify()
        flash(f"O carro com o Modelo {carromodelo} NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchCarro", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchCarro():
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
                            Carro.marca.like(f'%{term}%'),
                            Carro.modelo.like(f'%{term}%'),
                            Carro.ano.like(f'%{term}%'),
                            Carro.motor.like(f'%{term}%'),

                        )
                    )

                carros = (
                    Carro.query.filter(
                        *conditions
                    )
                    .order_by(Carro.marca.desc())
                    .paginate(page=page, per_page=10)
                )
            else:
                carros = (
                    Carro.query.filter(getattr(Carro, escolha).like(search))
                    .order_by(Carro.marca.desc())
                    .paginate(page=page, per_page=10)
                )

            return render_template(
                "/Carros/carros.html",
                carros=carros,
                busca=busca,
                escolha=escolha,
            )
        else:
            return redirect("/carros")
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)
