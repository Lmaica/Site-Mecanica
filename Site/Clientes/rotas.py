from flask import (
    redirect,
    render_template,
    url_for,
    flash,
    request,
    current_app,
    jsonify,
)
from Site import app, bcrypt, db, photos, nome_required, verificacao_nivel
from Site.Global.fun_global import  Edit_global, Redutor_codigo
from .modelos import Cliente, Veiculo
from .formularios import ForCliente, ForVeiculo
import secrets
from Site.Carros.modelos import Carro
import os
from flask_login import login_required, current_user
from Site.Serviços.modelos import Serviso
import json
import random
import string
from datetime import datetime, timezone
from sqlalchemy import desc, or_
from faker import Faker

#send_file
@app.route("/lopClientesVeiculos/<int:numero>")
@login_required
@nome_required
@verificacao_nivel(3)
def lopClientesVeiculos(numero):
    fake = Faker('pt_BR')

    def formatar_data(data):
        return datetime.strptime(data, '%d/%m/%Y').date()

    def gerar_cliente():
        tipo_cliente = random.choice(['pessoa_fisica', 'pessoa_juridica'])

        if tipo_cliente == 'pessoa_fisica':
            cadastrar = Cliente(
                nome=fake.name().upper(),
                fone=f"({fake.random_int(10, 99)}) {fake.random_int(90000, 99999)}-{fake.random_int(1000, 9999)}",
                fone1=f"({fake.random_int(10, 99)}) {fake.random_int(90000, 99999)}-{fake.random_int(1000, 9999)}",
                email=fake.email(),
                niver=formatar_data(fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%d/%m/%Y')),
                cpf=fake.cpf(),
                rg=fake.random_number(digits=8),
                cep=fake.postcode(),
                estado=fake.state_abbr(),
                cidade=fake.city(),
                bairro=fake.word().upper(),
                rua=fake.street_name().upper(),
                nuCasa=fake.building_number(),
                complemento=fake.word().upper(),
                foto="foto.jpg",
                statu="ATIVO",
                pjoucpf=0
            )
        elif tipo_cliente == 'pessoa_juridica':
            cadastrar = Cliente(
                nome=fake.name().upper(),
                razaoSocial=fake.company().upper(),
                nomeFantasia=fake.company().upper(),
                cnpj=fake.cnpj(),
                fone=f"({fake.random_int(10, 99)}) {fake.random_int(90000, 99999)}-{fake.random_int(1000, 9999)}",
                fone1=f"({fake.random_int(10, 99)}) {fake.random_int(90000, 99999)}-{fake.random_int(1000, 9999)}",
                email=fake.company_email(),
                niver=formatar_data(fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%d/%m/%Y')),
                cep=fake.postcode(),
                estado=fake.state_abbr(),
                cidade=fake.city(),
                bairro=fake.word().upper(),
                rua=fake.street_name().upper(),
                nuCasa=fake.building_number(),
                complemento=fake.word().upper(),
                foto="foto.jpg",
                statu="ATIVO",
                pjoucpf=1
            )
        else:
            raise ValueError("Tipo de cliente inválido.")

        db.session.add(cadastrar)
        return cadastrar

    def gerar_chassi_ficticio():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=17))

    def gerar_placa_ficticia(placas_usadas):
        placa = None
        while placa is None or placa in placas_usadas:
            letras = random.choices(string.ascii_uppercase, k=3)
            numeros = random.choices(string.digits, k=4)
            placa = f"{''.join(letras)}-{'' .join(numeros)}"
        placas_usadas.add(placa)
        return placa

    def criar_carros_para_clientes(lista_carros, lista_clientes):
        if not lista_carros or not lista_clientes:
            return None

        placas_usadas = set()

        for cliente in lista_clientes:
            carro = random.choice(lista_carros)
            placa = gerar_placa_ficticia(placas_usadas)
            km = random.randint(0, 100000)
            chassi = gerar_chassi_ficticio()

            veiculo = Veiculo(
                placa=placa,
                carro_id=carro.id,
                km=km,
                cliente_id=cliente.id,
                chassi=chassi,
            )

            db.session.add(veiculo)

        db.session.commit()
        return "Carros criados com sucesso para os clientes."

    
    clientes = [gerar_cliente() for _ in range(numero)]
    db.session.commit()

    lista_carros = Carro.query.all()
    lista_clientes = Cliente.query.all()
    criar_carros_para_clientes(lista_carros, lista_clientes)

    return redirect("/clientes")

    
@app.route("/clientes")
@login_required
@nome_required
@verificacao_nivel(3)
def clientes():
        
        page = request.args.get("page", 1, type=int)
        clientes = Cliente.query.order_by(Cliente.id.desc()).paginate(
            page=page, per_page=10
        )
        veiculos = Veiculo.query.all()
        return render_template(
            "Clientes/cliente.html", clientes=clientes, veiculos=veiculos
        )
 

@app.route("/addCliente", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addCliente():
    try:
        form = ForCliente()
        if form.validate_on_submit():
            checkbox_value = form.pjoucpf.data
            hash_senha = bcrypt.generate_password_hash("ATLJMAICA")
            campos_verificacao = [
                ("cpf", "O CPF {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("rg", "O RG {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("email", "O Email {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("cnpj", "O CNPJ {} Pertence ao Usuario ID {} Razão Social {}!!!"),
                (
                    "razaoSocial",
                    "O Razão Social {} Pertence ao Usuario ID {} CNPJ {}!!!",
                ),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
            ]

            condicao_encontrada = True
            for campo, mensagem in campos_verificacao:
                valor_campo = getattr(form, campo).data
                condicao_encontrada = Redutor_codigo.verificar_existencia(
                    Cliente, campo, valor_campo, "0", mensagem
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
                if checkbox_value == True:
                    razaoSocial = form.razaoSocial.data.upper().strip()
                    nomeFantasia = form.nomeFantasia.data.upper().strip()
                    cnpj = form.cnpj.data.strip()
                else:
                    razaoSocial = ""
                    nomeFantasia = ""
                    cnpj = ""
                cadastrar = Cliente(
                    nome=form.nome.data.upper().strip(),
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
                    statu=form.statu.data,
                    pjoucpf=checkbox_value,
                )
                db.session.add(cadastrar)
                db.session.commit()
                flash(f"O Cliente, Foi Cadastrado com Sucesso!!!", "cor-ok")
                return redirect(url_for("clientes"))
        elif request.method == 'POST':
            error_messages = ""
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{error}<br>"
            flash(error_messages, 'cor-alerta')
        return render_template("/Clientes/addClientes.html", form=form)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizcliente/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizcliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        form = ForCliente(request.form)
        if form.validate_on_submit():
            checkbox_value = form.pjoucpf.data
            campos_verificacao = [
                ("cpf", "O CPF {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("rg", "O RG {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("email", "O Email {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("cnpj", "O CNPJ {} Pertence ao Usuario ID {} Razão Social {}!!!"),
                (
                    "razaoSocial",
                    "O Razão Social {} Pertence ao Usuario ID {} CNPJ {}!!!",
                ),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
                ("fone1", "O Telefone {} Pertence ao Usuario ID {} Nome {}!!!"),
            ]

            condicao_encontrada = True
            for campo, mensagem in campos_verificacao:
                valor_campo = getattr(form, campo).data
                condicao_encontrada = Redutor_codigo.verificar_existencia(
                    Cliente, campo, valor_campo, cliente.id, mensagem
                )
                if not condicao_encontrada:
                    break
            if condicao_encontrada:
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
                if checkbox_value == False:
                    form.razaoSocial.data = ""
                    form.nomeFantasia.data = ""
                    form.cnpj.data = ""
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
                    "statu",
                    "complemento",
                ]

                for attribute in attributes:
                    setattr(
                        cliente,
                        attribute,
                        getattr(form, attribute).data.upper().strip(),
                    )

                cliente.email = form.email.data.strip()
                cliente.pjoucpf = form.pjoucpf.data
                db.session.commit()
                flash(f"O Cliente, Foi Atulizado com Sucesso!!!", "cor-ok")
                return redirect("/clientes")
        elif request.method == 'POST':
            error_messages = ""
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{error}<br>"
            flash(error_messages, 'cor-alerta')
        attributes = [
            "nome",
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
            "statu",
            "complemento",
        ]

        for attribute in attributes:
            getattr(form, attribute).data = getattr(cliente, attribute)

        form.pjoucpf.data = cliente.pjoucpf

        return render_template("/Clientes/addClientes.html", cliente=cliente, form=form)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deletecliente/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deletecliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        if request.method == "POST":
            if cliente.cnpj == "":
                clientenome = cliente.nome
            else:
                clientenome = cliente.razaoSocial
            try:
                db.session.delete(cliente)
                db.session.commit()
                flash(f"O Cliente {clientenome} foi Deletada com Sucesso!!!", "cor-ok")
                try:
                    if cliente.foto != "foto.jpg":
                        os.remove(
                            os.path.join(
                                current_app.root_path, "static/imagens/" + cliente.foto
                            )
                        )
                    else:
                        pass
                except:
                    pass
                return jsonify()
            except:
                flash(
                    f"{clientenome} NÃo pode ser APAGADO, Sem Antes APAGAR os Os Carro cadatrados",
                    "cor-alerta",
                )
            return jsonify()

        flash(f"O cliente {clientenome} NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/search", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def search():

    if request.method == "POST":
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
        elif escolha == "todos":
            search_terms = search_value.split()
            veiculo_salve = []
            for term in search_terms:
                veiculo_salve.append(
                    or_(
                        Veiculo.placa.like(f'%{term}%'), 
                        Veiculo.carro.has(Carro.marca.like(f'%{term}%')),
                        Veiculo.carro.has(Carro.modelo.like(f'%{term}%')),
                        Veiculo.carro.has(Carro.ano.like(f'%{term}%')),
                        Veiculo.carro.has(Carro.motor.like(f'%{term}%')),
                        
                        Veiculo.cliente.has(Cliente.id.like(f'%{term}%')), 
                        Veiculo.cliente.has(Cliente.nome.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.fone.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.fone1.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.email.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.niver.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.razaoSocial.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.nomeFantasia.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.cnpj.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.cpf.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.rg.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.cep.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.estado.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.cidade.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.bairro.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.rua.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.nuCasa.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.complemento.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.data_criado.like(f'%{term}%')),
                        Veiculo.cliente.has(Cliente.statu.like(f'%{term}%')),
                    )
                )
            veiculos_sistema = (
                Veiculo.query.filter(
                    *veiculo_salve,
                )
                .all()
            )
            cliente_ids = []
            for veic in veiculos_sistema:
                cliente_ids.append(veic.cliente_id)

            clientes = (
                Cliente.query.filter(
                    Cliente.id.in_(cliente_ids),
                )
                .order_by(Cliente.data_criado.desc())
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
            clientes=clientes,
            veiculos=veiculos,
            busca=busca,
            escolha=escolha,
        )
    else:
        return redirect("/clientes")



# Veiculos
@app.route("/addVeiculo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def addVeiculo(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        if cliente.nome == "":
            clientenome = cliente.nome
        else:
            clientenome = cliente.razaoSocial
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        form = ForVeiculo()
        if form.validate_on_submit():
            marca = request.form.get("marca")
            modelo = request.form.get("modelo")
            ano = request.form.get("ano")
            motor = request.form.get("motor")
            car = Carro.query.filter(
                Carro.marca == marca,
                Carro.modelo == modelo,
                Carro.ano == ano,
                Carro.motor == motor,
            ).first()
            filtroplaca = Veiculo.query.filter_by(
                placa=form.placa.data.upper().strip()
            ).first()
            if filtroplaca:
                cientefilter = Cliente.query.filter_by(
                    id=filtroplaca.cliente_id
                ).first()
                flash(
                    f"O Veiculo da placa {filtroplaca.placa} Pertence ao Cliente do ID {cientefilter.id} Nome/Social {clientenome}!!!",
                    "cor-alerta",
                )
            else:
                veicu = Veiculo(
                    placa=form.placa.data.upper().strip(),
                    carro_id=car.id,
                    km=form.km.data,
                    cliente_id=cliente.id,
                    chassi=form.chassi.data,
                )
                db.session.add(veicu)
                db.session.commit()
                flash(f"O Veiculo, Foi Cadatrada com Sucesso!!!", "cor-ok")
                return redirect(url_for("clientes"))
        return render_template("/Clientes/addVeiculo.html", marcas=marcas, form=form)
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/atulizveiculo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def atulizveiculo(id):
    try:
        veiculo = Veiculo.query.get_or_404(id)
        form = ForVeiculo(request.form)

        if request.method == "POST":
            marca = request.form.get("marca")
            modelo = request.form.get("modelo")
            ano = request.form.get("ano")
            motor = request.form.get("motor")
            car = Carro.query.filter(
                Carro.marca == marca,
                Carro.modelo == modelo,
                Carro.ano == ano,
                Carro.motor == motor,
            ).first()
            attributes = ["placa", "km", "chassi"]
            filtroplaca = Veiculo.query.filter_by(
                placa=form.placa.data.upper().strip()
            ).first()
            if filtroplaca and filtroplaca.id != veiculo.id:
                cientefilter = Cliente.query.filter_by(
                    id=filtroplaca.cliente_id
                ).first()
                flash(
                    f"O Veiculo da placa {filtroplaca.placa} Pertence ao Cliente do ID {cientefilter.id} Nome/Social {cientefilter.nome}!!!",
                    "cor-alerta",
                )
            else:
                for attribute in attributes:
                    setattr(
                        veiculo,
                        attribute,
                        getattr(form, attribute).data.upper().strip(),
                    )

                veiculo.carro_id = car.id
                veiculo.cliente_id = veiculo.cliente_id

                db.session.commit()
                flash(f"O Veiculo, Foi Atulizado com Sucesso!!!", "cor-ok")
                return redirect("/clientes")

        idcarro = Carro.query.filter(Carro.id == veiculo.carro_id).first()
        marca = idcarro.marca
        modelo = idcarro.modelo
        ano = idcarro.ano
        motor = idcarro.motor
        marcas = Edit_global.remove_repetidos(
            [carro.marca for carro in Carro.query.distinct(Carro.marca).all()]
        )
        modelos = Carro.query.filter_by(marca=marca).distinct(Carro.modelo).all()
        modelos = Edit_global.remove_repetidos([model.modelo for model in modelos])
        anos = (
            Carro.query.filter_by(marca=marca, modelo=modelo).distinct(Carro.ano).all()
        )
        anos = Edit_global.remove_repetidos([ano.ano for ano in anos])
        motors = (
            Carro.query.filter_by(marca=marca, modelo=modelo, ano=ano)
            .distinct(Carro.motor)
            .all()
        )
        motors = Edit_global.remove_repetidos([motor.motor for motor in motors])
        attributes = ["placa", "km", "chassi"]

        for attribute in attributes:
            getattr(form, attribute).data = getattr(veiculo, attribute)

        return render_template(
            "/Clientes/addVeiculo.html",
            veiculo=veiculo,
            form=form,
            marcas=marcas,
            modelos=modelos,
            anos=anos,
            motors=motors,
            marc=marca,
            model=modelo,
            an=ano,
            moto=motor,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/deleteveiculo/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(4)
def deleteveiculo(id):
    try:
        veiculo = Veiculo.query.get_or_404(id)
        if request.method == "POST":
            veiculoplaca = veiculo.placa
            try:
                db.session.delete(veiculo)
                db.session.commit()
                flash(
                    f"O Veiculo com a Placa {veiculoplaca} foi Deletada com Sucesso!!!",
                    "cor-ok",
                )
                return jsonify()
            except:
                flash(
                    f"O Carro com a Placa {veiculoplaca} NÃo pode ser APAGADO, Sem Antes APAGAR as O.S referente ao Carro",
                    "cor-alerta",
                )
                return jsonify()
        flash(f"O Veiculo com a Placa {veiculoplaca} NÂO foi Deletada", "cor-alerta")
        return jsonify()
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/get_modelos", methods=["POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def get_modelos():
    marca = request.form["marca"]
    modelos = Carro.query.filter_by(marca=marca).distinct(Carro.modelo).all()
    modelos = Edit_global.remove_repetidos([model.modelo for model in modelos])
    return jsonify({"modelos": modelos})


@app.route("/get_anos", methods=["POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def get_anos():
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    anos = Carro.query.filter_by(marca=marca, modelo=modelo).distinct(Carro.ano).all()
    anos = Edit_global.remove_repetidos([ano.ano for ano in anos])
    anos_ordenados = sorted(anos, reverse=True)
    return jsonify({"anos": anos_ordenados})


@app.route("/get_motors", methods=["POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def get_motors():
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    ano = request.form["ano"]
    motors = (
        Carro.query.filter_by(marca=marca, modelo=modelo, ano=ano)
        .distinct(Carro.motor)
        .all()
    )
    motors = Edit_global.remove_repetidos([motor.motor for motor in motors])
    return jsonify({"motors": motors})


# filtros do cliente
@app.route("/servicoDoCliente/<int:id>")
@login_required
@nome_required
@verificacao_nivel(3)
def servicoDoCliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        page = request.args.get("page", 1, type=int)
        servisos = (
            Serviso.query.filter(Serviso.cliente_os == cliente)
            .filter(Serviso.status == "Finalizado")
            .filter(
                Serviso.id != 0
            ) 
            .order_by(Serviso.data_finalizada.desc())
            .paginate(page=page, per_page=10)
        )

        return render_template(
            "Serviços/Serviços.html",
            status="cliente",
            cliente_id=cliente,
            servisos=servisos,
        )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)


@app.route("/searchservicoDoCliente/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def searchservicoDoCliente(id):
    try:
        if request.method == "POST":
            cliente = Cliente.query.get_or_404(id)
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
                    .filter(Serviso.status == "Finalizado", Serviso.cliente_os == cliente)
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
            elif escolha == "modelo":
               servisos = (
                    Serviso.query.join(Veiculo).join(Carro)
                    .filter(Carro.modelo.like(search))
                    .filter(Serviso.status == "Finalizado", Serviso.cliente_os == cliente)
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
                            Serviso.cliente_os == cliente,
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
                            Serviso.cliente_os == cliente,
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
                    .filter(Serviso.status == "Finalizado", Serviso.cliente_os == cliente)
                    .order_by(Serviso.data_finalizada.desc())
                    .paginate(page=page, per_page=10)
                )
            return render_template(
                "Serviços/Serviços.html",
                status="cliente",
                cliente_id =cliente,
                servisos=servisos,
                busca=busca,
                escolha=escolha,
            )
    except Exception as erro:
        MSG = f"Erro {erro}!!! Desculpe mais algo deu errado,volte a pagina inicial e Tente Novamente!!!"
        return render_template("pagina_erro.html", MSG=MSG)

# Criar cerviço para carro
@app.route("/fazer_os_carro/<int:id>")
@login_required
@nome_required
@verificacao_nivel(3)
def fazer_os_carro(id):
    user = current_user
    veiculo = Veiculo.query.get_or_404(id)
    num_items = Serviso.query.count()
    if num_items == 0:
        Redutor_codigo.Redutor_codigo_seriviços(veiculo.cliente_id, veiculo.id, user.id)
        return redirect(f"/AbrirServiço/1/tratatar")
    filtro = Serviso.query.order_by(desc(Serviso.id)).first()
    get_serviso = Serviso.query.get_or_404(filtro.id)
    Cliente_os_atual = json.loads(get_serviso.cliente_veiculo)
    if len(Cliente_os_atual["itens"]) == 0 and get_serviso.cliente_os_id == 0:
        get_serviso.cliente_os_id = veiculo.cliente_id
        get_serviso.veiculo_os_id = veiculo.id
        get_serviso.user_os_id = user.id
        get_serviso.data_finalizada = datetime.now(timezone.utc).astimezone()
        get_serviso.data_finalizada = datetime.now(timezone.utc).astimezone()
        db.session.commit()
    else:
        Redutor_codigo.Redutor_codigo_seriviços(veiculo.cliente_id, veiculo.id, user.id)
    filtro = Serviso.query.order_by(desc(Serviso.id)).first()
    Serviço = filtro
    return redirect(f"/AbrirServiço/{Serviço.id}/tratatar")

#dados dinamicos de serviços do cliente
@app.route("/carDinamicos/<int:id>", methods=["GET", "POST"])
@login_required
@nome_required
@verificacao_nivel(3)
def carDinamicos(id):
    cliente = Cliente.query.get_or_404(id)
    servisos = (
        Serviso.query.filter(Serviso.cliente_os == cliente)
        .filter(Serviso.status == "Finalizado")
        .filter(
            Serviso.id != 0
        ) 
        .order_by(Serviso.data_finalizada.desc())
    )
    return render_template(
        "/clientes/dadosDinamicos.html",        
        status="cliente",
        cliente_id=cliente,
        servisos=servisos,
    )


