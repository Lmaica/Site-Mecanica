from flask import render_template, request, redirect, url_for, flash, jsonify
from Site import db
from datetime import datetime
import json
from Site.Servicos.modelos import Serviso
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class Calculos_gloabal:
    def format_valor_moeda(valor):
        formatted_value = "{:,.2f}".format(valor)
        formatted_value = "R$" + formatted_value.replace(",", ";").replace(".", ",").replace(";", ".")
        return formatted_value


    def valor_para_Calculos(valor_str):
        return float(
            valor_str.replace(".", "")
            .replace(" ", "")
            .replace("\xa0", "")
            .replace("R$", "")
            .replace(",", ".")
        )

    def calcular_diferenca_percentual(valor_antigo, valor_novo):
        diferenca = valor_novo - valor_antigo
        diferenca_percentual = (diferenca / valor_antigo) * 100
        return diferenca_percentual

    def calcular_valor_porcentagem(valor_base, porcentagem):
        valor_alterado = valor_base + (valor_base * porcentagem / 100)
        return valor_alterado


class Redutor_codigo:
    def enviar_email_confirmar(usuario, nova_senha,confirmar,serviso):
        remetente = 'maica.contato@outlook.com' 
        destinatario = usuario
        if confirmar == "CONFIRME":
            assunto = "Confirmação de Conta"
            reset_url = url_for('confirm_email',usuario=usuario ,token=nova_senha, _external=True)
            mensagem  = f"""
                <p>Olá!</p>
                <p>Para Criar Sua conta, clique no link abaixo:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>O link expirará em 24 horas.</p>
                <p>Se você tiver problemas ao clicar no link, copie e cole o seguinte URL em seu navegador:</p>
                <p>{reset_url}</p>
                <p>Atenciosamente,</p>
                <p>Equipe de Suporte</p>"""
        elif confirmar == 'APROVAR':
            assunto = "Aprovar Serviço"
            reset_url = url_for('aprovacao',usuario=usuario ,token=nova_senha,serviso=serviso.id, _external=True)
            mensagem  = f"""
                <p>Olá!</p>
                <p>Para aprovar o serviço N:{serviso.id}, clique no link abaixo:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>O link expirará em 24 horas.</p>
                <p>Se você tiver problemas ao clicar no link, copie e cole o seguinte URL em seu navegador:</p>
                <p>{reset_url}</p>
                <p>Atenciosamente,</p>
                <p>Equipe de Suporte</p>"""
        else:
            assunto = "Reconfiguração de Senha"
            reset_url = url_for('resete_senha', usuario=usuario, token=nova_senha, _external=True)
            mensagem = f"""
                <p>Olá!</p>
                <p>Para reconfigurar sua senha, clique no link abaixo:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>O link expirará em 24 horas.</p>
                <p>Se você tiver problemas ao clicar no link, copie e cole o seguinte URL em seu navegador:</p>
                <p>{reset_url}</p>
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

        with smtplib.SMTP(servidor_smtp, porta) as servidor:
            servidor.starttls()
            servidor.login(usuario_smtp, senha_smtp)
            servidor.send_message(msg)
    def handle_generic_add(request, model, attribute_name, redirect_route):
        try:
            if request.method == "POST":
                attribute_value = request.form.get("nome").upper().strip()
                filters = model.query.filter_by(
                    **{attribute_name: attribute_value}
                ).first()
                if filters:
                    flash(
                        f"O {attribute_name} {attribute_value} já está cadastrado!!!",
                        "cor-alerta",
                    )
                else:
                    new_object = model(**{attribute_name: attribute_value})
                    db.session.add(new_object)
                    flash(
                        f"{attribute_name.capitalize()} {attribute_value} foi cadastrado",
                        "cor-ok",
                    )
                    db.session.commit()
                    return redirect(url_for(redirect_route))
            return render_template(
                "/addUmDado.html",
                dado="",
                perfil=redirect_route,
                produto=f"{redirect_route.replace('_',' ')}",
            )
        except Exception as erro:
            MSG = f"Erro {erro}!!! Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
            return render_template("pagina_erro.html", MSG=MSG)

    def handle_generic_update(request, model, id, attribute_name, redirect_route):
        try:
            object_to_update = model.query.get_or_404(id)
            if request.method == "POST":
                attribute_value = request.form.get("nome").upper().strip()
                filter = model.query.filter_by(
                    **{attribute_name: attribute_value}
                ).first()
                if filter and filter.id != id:
                    flash(
                        f"O {attribute_name} {attribute_value} já está cadastrado!!!",
                        "cor-alerta",
                    )
                else:
                    setattr(object_to_update, attribute_name, attribute_value)
                    db.session.commit()
                    flash(
                        f"{attribute_name.capitalize()} foi atualizado com sucesso!!!",
                        "cor-ok",
                    )
                    return redirect(url_for(redirect_route))
            return render_template(
                "/addUmDado.html",
                dado=object_to_update,
                atulizar="atulizar",
                perfil=redirect_route,
                produto=f"{redirect_route.replace('_',' ')}",
            )
        except Exception as erro:
            MSG = f"Erro {erro}!!! Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
            return render_template("pagina_erro.html", MSG=MSG)

    def handle_generic_delete(request, model, id, attribute_name, redirect_route):
        try:
            object_to_delete = model.query.get_or_404(id)
            if request.method == "POST":
                attribute_value = object_to_delete.__dict__[attribute_name]
                try:
                    db.session.delete(object_to_delete)
                    db.session.commit()
                    flash(
                        f"O {attribute_name} {attribute_value} foi deletado com sucesso!!!",
                        "cor-ok",
                    )
                    return jsonify()
                except:
                    flash(
                        f"O {attribute_value} não pode ser apagado. Modifique-o em vez de apagar, pois há registros associados a esse {attribute_name}!",
                        "cor-alerta",
                    )
                    return jsonify()
            flash(
                f"O {attribute_name} com o nome {attribute_value} não foi deletado",
                "cor-alerta",
            )
            return jsonify()
        except Exception as erro:
            MSG = f"Erro {erro}!!! Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
            return render_template("pagina_erro.html", MSG=MSG)

    def search_generic(model, perfil):
        try:
            if request.method == "POST":
                page = request.args.get("page", 1, type=int)
                form = request.form
                search_value = form["search_string"].upper()
                search = f"%{search_value}%"
                escolha = str(request.form.get("searchselector"))
                busca = search_value = form["search_string"]

                results = (
                    model.query.filter(getattr(model, escolha).like(search))
                    .order_by(model.id.desc())
                    .paginate(page=page, per_page=10)
                )

                return render_template(
                    "/umDado.html",
                    perfils=results,
                    busca=busca,
                    escolha=escolha,
                    perfil=perfil,
                    produto=f"{perfil.replace('_',' ')}",
                )
            else:
                return redirect(f"/{perfil.lower()}")
        except Exception as erro:
            MSG = f"Erro {erro}!!! Desculpe, algo deu errado. Volte à página inicial e tente novamente!!!"
            return render_template("pagina_erro.html", MSG=MSG)

    def verificar_existencia(modelo, campo, valor, id_atual, mensagem):
        condicao_encontrada = False
        filtro = modelo.query.filter_by(**{campo: valor.strip()}).first()
        if filtro and getattr(filtro, campo) and filtro.id != id_atual:
            flash(
                mensagem.format(getattr(filtro, campo), filtro.id, filtro.nome),
                "cor-alerta",
            )
            condicao_encontrada = False
        else:
            condicao_encontrada = True
        return condicao_encontrada

    def extract_data(serviso, get_Cliente, search_value):
        items_data_servicos = []
        for servico in serviso:
            cliente_os = json.loads(servico.cliente)
            veiculo_os = json.loads(servico.veiculo)
            for item in cliente_os["itens"]:
                serv_nome_cliente = item.get("nome")
                cli_id = item.get("cli_id")
                if serv_nome_cliente is not None:
                    items_data_servicos.append(
                        {
                            "id": servico.id,
                            "nome": serv_nome_cliente,
                            "status": servico.status,
                            "data": servico.data_criado,
                            "dataFin": servico.data_finalizada,
                        }
                    )
                else:
                    for getCli in get_Cliente:
                        for item_vei in veiculo_os["itens"]:
                            veic_id = item_vei.get("veic_id")
                            if int(getCli.id) == int(cli_id):
                                items_data_servicos.append(
                                    {
                                        "id": servico.id,
                                        "id_cliente": getCli.id,
                                        "nome": getCli.nome,
                                        "veiculo_id": veic_id,
                                        "status": servico.status,
                                        "data": servico.data_criado,
                                        "dataFin": servico.data_finalizada,
                                    }
                                )

        return items_data_servicos

    def Redutor_codigo_seriviços(cliente_os_id, veiculo_os_id, user_os_id):
        dadosJson = {"itens": []}
        get_Serviso = Serviso(
            status="Orçamento",
            cliente_veiculo=json.dumps(dadosJson),
            peca_os=json.dumps(dadosJson),
            mo_os=json.dumps(dadosJson),
            cliente_os_id=cliente_os_id,
            veiculo_os_id=veiculo_os_id,
            carteira_id=json.dumps(dadosJson),
            mecanico_id=0,
            vendedor_id=0,
            user_os_id=user_os_id,
            data_criado=datetime.now(timezone.utc).astimezone(),
            data_finalizada=datetime.now(timezone.utc).astimezone(),
        )
        db.session.add(get_Serviso)
        db.session.commit()


class Edit_global:
    def remove_repetidos(lista):
        l = []
        for i in lista:
            if i not in l:
                l.append(i)
        return l

    def data_hora():
        data_atual = datetime.datetime.now()
        ano = data_atual.year
        mes = data_atual.month
        dia = data_atual.day
        hora = data_atual.hour
        minuto = data_atual.minute
        segundo = data_atual.second
        return ano, mes, dia, hora, minuto, segundo
