var menu = document.getElementById('menu');
var content = document.getElementById('content');
if (!content) {
    content = document.getElementById('content-consumidor');
}
var menuButton = document.getElementById('menuButton');
var NavAdmin = document.getElementById('NavAdmin');
var DadosBaixo = document.getElementById('DadosBaixo');
if (!DadosBaixo) {
    DadosBaixo = document.getElementById('DadosAcimaConsumidor');
}
window.addEventListener("beforeunload", function () {
    showLoader();
});


function showLoader() {
    document.getElementById("loader").style.display = "block";
    menu.classList.add('no-click');
    content.classList.add('no-click');
    menuButton.classList.add('no-click');
    NavAdmin.classList.add('no-click');
    DadosBaixo.classList.add('no-click');
    setTimeout(function () {
        location.reload();
    }, 10000);

}


// Atulizar Configuração
$(document).ready(function () {
    var dados = {};
    var body = document.body;
    var principalCorMesclada = document.getElementsByClassName('principalCorMesclada');
    var principalCorUnica = document.getElementsByClassName('principalCorUnica');
    var cabeçarioPagina = document.getElementsByClassName('cabeçario-pagina');

    $.ajax({
        type: 'POST',
        url: '/dados_cofigurarar',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(dados),
        success: function (response) {
            for (var i = 0; i < cabeçarioPagina.length; i++) {
                cabeçarioPagina[i].style.background = response.cores.principal_secundaria;
                cabeçarioPagina[i].style.color = response.cores.principal_letras;

            }
            for (var i = 0; i < principalCorUnica.length; i++) {
                principalCorUnica[i].style.background = response.cores.principal_botao;
                principalCorUnica[i].style.color = response.cores.principal_letras;
                var aElements = principalCorUnica[i].querySelectorAll('a');
                var imagem = principalCorUnica[i].querySelector('img');

                if (imagem) {
                    imagem.style.filter = 'invert(' + response.icones.img_cor + '%)';
                }

                aElements.forEach(function (a) {
                    a.style.color = response.cores.principal_letras;
                });

            }
            for (var i = 0; i < principalCorMesclada.length; i++) {
                principalCorMesclada[i].style.background = response.cores.principal_secundaria;;
                principalCorMesclada[i].style.color = response.cores.principal_letras;
                var imagem = principalCorMesclada[i].querySelector('img');
                if (imagem) {
                    imagem.style.filter = 'invert(' + response.icones.img_cor + '%)';
                }
            }

            body.style.fontFamily = response.fontes.fonte_principal;
        },
        error: function (error) {
            console.error('Erro:', error);
        }
    });
});

//trazer dados do banco para o seletor 
$(document).ready(function () {
    // Carregar modelos com base na marca selecionada
    $('#marca').change(function () {
        var marca = $(this).val();
        if (marca) {
            $('#modelo').prop('disabled', false);
            $.ajax({
                url: '/get_modelos',
                type: 'POST',
                data: { marca: marca },
                success: function (data) {
                    $('#modelo').html('<option value="">--Selecione modelo--</option>');
                    data.modelos.forEach(function (modelo) {
                        $('#modelo').append('<option value="' + modelo + '">' + modelo + '</option>');
                    });
                }
            });
            $('#ano').html('<option value="">--Selecione ano--</option>');
            $('#ano').prop('disabled', true);
            $('#motor').html('<option value="">--Selecione motor--</option>');
            $('#motor').prop('disabled', true);
        }
    });

    // Carregar anos com base no modelo selecionado
    $('#modelo').change(function () {
        var marca = $('#marca').val();
        var modelo = $(this).val();
        if (modelo) {
            $('#ano').prop('disabled', false);
            $.ajax({
                url: '/get_anos',
                type: 'POST',
                data: { marca: marca, modelo: modelo },
                success: function (data) {
                    $('#ano').html('<option value="">--Selecione ano--</option>');
                    data.anos.forEach(function (ano) {
                        $('#ano').append('<option value="' + ano + '">' + ano + '</option>');
                    });
                }
            });
            $('#motor').html('<option value="">--Selecione motor--</option>');
            $('#motor').prop('disabled', true);
        }
    });

    // Carregar motores com base no ano selecionado
    $('#ano').change(function () {
        var marca = $('#marca').val();
        var modelo = $('#modelo').val();
        var ano = $(this).val();
        if (ano) {
            $('#motor').prop('disabled', false);
            $.ajax({
                url: '/get_motors',
                type: 'POST',
                data: { marca: marca, modelo: modelo, ano: ano },
                success: function (data) {
                    $('#motor').html('<option value="">--Selecione motor--</option>');
                    data.motors.forEach(function (motor) {
                        $('#motor').append('<option value="' + motor + '">' + motor + '</option>');
                    });
                }
            });
        }
    });

});
// CARROS PARA SERVIÇOS E PEAS
$(document).ready(function () {
    // Carregar modelos com base na marca selecionada

    $('#marcaT').change(function () {
        var marca = $(this).val();
        if (marca) {
            $('#modeloT').prop('disabled', false);
            $.ajax({
                url: '/get_modelosServ',
                type: 'POST',
                data: { marca: marca },
                success: function (data) {
                    $('#modeloT').html('<option value="TODOS">--Selecione modelo--</option>');
                    data.modelo.forEach(function (modelo) {
                        $('#modeloT').append('<option value="' + modelo + '">' + modelo + '</option>');
                    });
                }
            });
            $('#anoIniT').html('<option value="TODOS">--Selecione Do ano--</option>');
            $('#anoIniT').prop('disabled', true);
            $('#anoFinT').html('<option value="TODOS">--Selecione Ate o ano--</option>');
            $('#anoFinT').prop('disabled', true);
            $('#motorT').html('<option value="TODOS">--Selecione motor--</option>');
            $('#motorT').prop('disabled', true);
        }
    });

    // Carregar anos com base no modelo selecionado
    $('#modeloT').change(function () {
        var marca = $('#marcaT').val();
        var modelo = $(this).val();
        if (modelo) {
            $('#anoIniT').prop('disabled', false);
            $.ajax({
                url: '/get_anosIni',
                type: 'POST',
                data: { marca: marca, modelo: modelo },
                success: function (data) {
                    $('#anoIniT').html('<option value="TODOS">--Selecione Do ano--</option>');
                    data.anosIni.forEach(function (anoIni) {
                        $('#anoIniT').append('<option value="' + anoIni + '">' + anoIni + '</option>');
                    });
                }
            });
            $('#anoFinT').html('<option value="TODOS">--Selecione Ate o ano--</option>');
            $('#anoFinT').prop('disabled', true);
            $('#motorT').html('<option value="TODOS">--Selecione motor--</option>');
            $('#motorT').prop('disabled', true);
        }
    });
    // Carregar anoFin com base no anoIni
    $('#anoIniT').change(function () {
        var marca = $('#marcaT').val();
        var modelo = $('#modeloT').val();
        var anoIni = $(this).val();
        if (anoIni) {
            $('#anoFinT').prop('disabled', false);
            $.ajax({
                url: '/get_anosFin',
                type: 'POST',
                data: { marca: marca, modelo: modelo, anoIni: anoIni },
                success: function (data) {
                    $('#anoFinT').html('<option value="TODOS">--Selecione Ate o ano--</option>');
                    data.anosFin.forEach(function (anoFin) {
                        $('#anoFinT').append('<option value="' + anoFin + '">' + anoFin + '</option>');
                    });
                }
            });
            $('#motorT').html('<option value="TODOS">--Selecione motor--</option>');
            $('#motorT').prop('disabled', true);
        }
    });
    // Carregar motores com base no ano selecionado
    $('#anoFinT').change(function () {
        var marca = $('#marcaT').val();
        var modelo = $('#modeloT').val();
        var anoIni = $('#anoIniT').val();
        var anoFin = $(this).val();

        if (anoFin) {
            $('#motorT').prop('disabled', false);
            $.ajax({
                url: '/get_motorsServ',
                type: 'POST',
                data: { marca: marca, modelo: modelo, anoIni: anoIni, anoFin: anoFin },
                success: function (data) {
                    $('#motorT').html('<option value="TODOS">--Selecione motor--</option>');
                    data.motors.forEach(function (motor) {
                        $('#motorT').append('<option value="' + motor + '">' + motor + '</option>');

                    });
                }
            });
        }
    });
});

//Adicionar Carro no multiplo select2
$(document).ready(function () {
    $('#add-button').on('click', function (event) {
        event.preventDefault();
        var option1 = $('#marcaT').val();
        var option2 = $('#modeloT').val();
        var option3 = $('#anoIniT').val();
        var option4 = $('#anoFinT').val();
        var option5 = $('#motorT').val();
        var newOptionValue = option1 + '/' + option2 + '/' + option3 + '/' + option4 + '/' + option5;
        var newOptionExists = $('#carros option[value="' + newOptionValue + '"]').length > 0;
        if (!newOptionExists) {
            var newOption = new Option(newOptionValue, newOptionValue, true, true);
            $('#carros').append(newOption).trigger('change');
        }
    });
});

//Estilo Select2 para todos os select
$(document).ready(function () {

    $('select').addClass('select2');
    $('.searchselector').removeClass('select2');
    $('.searchselector').css('max-width', '100%');

    $('select.select2').select2({
        width: '100%',
    });

    $('.select2-container').css('max-width', '100%');

});


//Valor da Mão de obra dinamicamente.
$(document).ready(function () {
    $('#hora').change(function () {
        var hora = $(this).val();
        if (hora) {
            $.ajax({
                url: '/valorHora',
                type: 'POST',
                data: { hora: hora },
                success: function (data) {
                    var soma = data.soma;
                    $('#preso').val(soma);
                }
            });
        }
    });
});


// Função para atualizar o preço total quando o valor do input muda
function formatCurrency(value) {
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function getPrice(element) {
    return parseFloat(element.textContent.replace(/[^\d.,]/g, '').replace('.', '').replace(',', '.').trim());
}

function updatePriceTotal(inputElement, precoElementPecas) {
    const input = inputElement.value;

    if (precoElementPecas) {
        const preco = getPrice(precoElementPecas);
        const precoTotalPeca = input * preco;
        const precoTotalPecaElement = inputElement.closest(".containerDados").querySelector(".preco-total");
        precoTotalPecaElement.innerHTML = `<strong style='color: #000000;'>Preço Total:</strong> ${formatCurrency(precoTotalPeca)}`;
    }
}

function atualizarTotais() {
    let totalPecas = 0;
    let totalMDO = 0;

    const elementosPeca = document.querySelectorAll('.precoPeca');

    elementosPeca.forEach(function (elemento) {
        const precoPeca = getPrice(elemento);
        const quantidadeInput = elemento.closest('.containerDados').querySelector('.number-input');
        const quantidade = parseFloat(quantidadeInput.value);
        totalPecas += precoPeca * quantidade;
    });

    const elementosMDO = document.querySelectorAll('.precoMDO');
    elementosMDO.forEach(function (elemento) {
        totalMDO += getPrice(elemento);
    });

    const totalGeral = totalPecas + totalMDO;
    document.getElementById('soma_pecas').innerHTML = `<p style="float: right;">Total em Pecas: <strong>${formatCurrency(totalPecas)}</strong></p>`;
    document.getElementById('somaTotal').innerHTML = `<strong>Total:</strong> ${formatCurrency(totalGeral)}`;
    var valordaspesas = document.getElementById('valordaspesas');
    if (valordaspesas) {
        valordaspesas.value = `${formatCurrency(totalPecas)}`;
    }

    var valortodos = document.getElementById('valortodos');
    if (valortodos) {
        valortodos.value = `${formatCurrency(totalGeral)}`;
    }

}

document.addEventListener("DOMContentLoaded", function () {
    const soma_pecas = document.getElementById("soma_pecas");
    const inputs = document.querySelectorAll(".containerDados input[type='number']");

    inputs.forEach(function (input) {
        const container = input.closest(".containerDados");
        const precoElementPecas = container.querySelector(".precoPeca");
        updatePriceTotal(input, precoElementPecas);

        input.addEventListener("input", function () {
            updatePriceTotal(input, precoElementPecas);
            atualizarTotais();
        });
    });

    document.addEventListener('input', function (event) {
        const target = event.target;

        if (target.classList.contains('number-input') || target.classList.contains('precoMDO') || target.classList.contains('precoPeca')) {
            atualizarTotais();
        }
    });

    if (soma_pecas) {
        atualizarTotais();
    } else {
    }
});


// Função para atualizar a quantidade de peças
function atualizarQuantidadePecas(inputElement) {
    var novo_valor_un = $(inputElement).val();
    var item_id = $(inputElement).data("item-id");
    var servico_id = $("#Ser_id").val();
    $.ajax({
        url: "/atualizar_uni_pecas/" + servico_id + "/" + item_id,
        method: "PUT",
        data: { un: novo_valor_un },
        error: function () {
            console.log("Erro ao atualizar o item");
        }
    });
}

// Função para atualizar o lado das peças
function atualizarLadoPecas(selectElement) {
    var novo_valor_lado = $(selectElement).val();
    var item_id = $(selectElement).data("item-id");
    var servico_id = $("#Ser_id").val();
    $.ajax({
        url: "/atualizar_lado_pecas/" + servico_id + "/" + item_id,
        method: "PUT",
        data: { lado: novo_valor_lado },
        error: function () {
            console.log("Erro ao atualizar o item");
        }
    });
}

//Obrigar a colocar nome ou telefone ou email
function validarCampos() {
    var clientName = document.getElementById("clientName").value;
    var phoneNumber = document.getElementById("telefone").value;
    var email = document.getElementById("email").value;
    var missingFields = [];

    if (clientName === "") {
        missingFields.push("(Nome do Cliente)");
    }

    if (phoneNumber === "" && email === "") {
        missingFields.push("(Telefone ou Email)");
    }

    if (missingFields.length > 0) {
        MensagemServiço = document.getElementById('MensagemServiço')
        MensagemServiço.classList.remove('retira');
        document.getElementById('MensagemServiço').innerHTML = `Por favor, preencha os seguintes campos obrigatórios:<br>${formatCurrency(missingFields)}`;
        return false;
    }

    return true;
}

//atulizar cliente no Orçamento
$(document).ready(function () {
    $(".DadosClienteServico").on("input", function () {
        var Ser_id = $("#Ser_id").val();
        var campos = ["clientName", "telefone", "email", "placa", "Ser_marca", "Ser_modelo", "Ser_ano", "Ser_motor", "km"];

        var valores = {};
        campos.forEach(function (campo) {
            valores[campo] = $("#" + campo).val() || 'TRATAMENTO';
        });

        $.ajax({
            url: "/atualizar_cliente_os/" + Ser_id + "/" + valores.clientName + "/" + valores.telefone + "/" + valores.email + "/" + valores.placa + "/" + valores.Ser_marca + "/" + valores.Ser_modelo + "/" + valores.Ser_ano + "/" + valores.Ser_motor + "/" + valores.km,
            method: "PUT",
            error: function () {
                console.log("Erro ao atualizar o item");
            }
        });
    });
});

//atulizar obsSer no Orçamento
$(document).ready(function () {
    $("#obsSer").on("input", function () {
        var Ser_id = $("#Ser_id").val();
        var obsSer = $("#obsSer").val();
        if (obsSer == '') {
            obsSer = 'TRATAMENTO';
        }
        $.ajax({
            url: "/atualizar_obs_os/" + Ser_id + "/" + obsSer,
            method: "PUT",
            error: function () {
                console.log("Erro ao atualizar o item");
            }
        });
    });
});

//atulizar Vendedor no Orçamento
$(document).ready(function () {
    $("#vendedor").on("change", function () {
        var Ser_id = $("#Ser_id").val();
        var vendedor = $("#vendedor").val();
        $.ajax({
            url: "/atualizar_vendedor_os/" + Ser_id + "/" + vendedor,
            method: "PUT",
            error: function () {
                console.log("Erro ao atualizar o item");
            }
        });
    });
});

//atulizar Mecanico no Orçamento
$(document).ready(function () {
    $("#mecanico").on("change", function () {
        var Ser_id = $("#Ser_id").val();
        var mecanico = $("#mecanico").val();
        $.ajax({
            url: "/atualizar_mecanico_os/" + Ser_id + "/" + mecanico,
            method: "PUT",
            error: function () {
                console.log("Erro ao atualizar o item");
            }
        });
    });
});

//Adicionar pecas ao orçamento sem atulizar a pagina
function enviarFormulario(idPeca, event) {
    event.preventDefault();

    var formulario = document.getElementById('meu-formulario-' + idPeca);
    var formData = new FormData(formulario);
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', '/adicinar_item_peca', true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                try {
                    var resposta = JSON.parse(xhr.responseText);
                    if (resposta.success) {
                        var message = resposta.message;
                        var cor = resposta.cor
                        var DivFlutante = document.createElement('div');
                        DivFlutante.innerHTML = `
                           <div id="DivFlutante">
                                <div class="${cor} DivFlutanteCabeça">
                                    <h3>AVISO!!!</h3>
                                    <span onclick="ButunDivFlutante()" class="close-btn">&times;</span>
                                </div>
                                <div class="DivFlutanteConte">
                                    <p>${message}</p>
                                </div>
                            </div>
                        `;
                        document.body.appendChild(DivFlutante);
                    } else {
                        alert("Erro ao adicionar peca: " + resposta.message);
                    }
                } catch (e) {
                    console.error("Erro ao analisar a resposta JSON:", e);
                    alert("Erro ao processar a resposta do servidor.");
                }
            } else {
                alert("Erro ao processar a solicitação. Tente novamente.");
            }
        }
    };

    xhr.send(formData);
}

//Adicionar Mão de obra ao orçamento sem atulizar a pagina
function enviarFormularioMDO(idMDO, event) {
    event.preventDefault();

    var formulario = document.getElementById('meu-formulario-' + idMDO);
    var formData = new FormData(formulario);

    var xhr = new XMLHttpRequest();
    xhr.open('PUT', '/adicinar_item_MaoObra', true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                try {
                    var resposta = JSON.parse(xhr.responseText);
                    if (resposta.success) {
                        var message = resposta.message;
                        var cor = resposta.cor
                        var DivFlutante = document.createElement('div');
                        DivFlutante.innerHTML = `
                           <div id="DivFlutante">
                                <div class="${cor} DivFlutanteCabeça">
                                    <h3>AVISO!!!</h3>
                                    <span onclick="ButunDivFlutante()" class="close-btn">&times;</span>
                                </div>
                                <div class="DivFlutanteConte">
                                    <p>${message}</p>
                                </div>
                            </div>
                        `;
                        document.body.appendChild(DivFlutante);
                    } else {
                        alert("Erro ao adicionar Mão de obra: " + resposta.message);
                    }
                } catch (e) {
                    console.error("Erro ao analisar a resposta JSON:", e);
                    alert("Erro ao processar a resposta do servidor.");
                }
            } else {
                alert("Erro ao processar a solicitação. Tente novamente.");
            }
        }
    };

    xhr.send(formData);
}
//Adicionar pecas ao Combo sem atulizar a pagina
function enviarFormularioCombo(idPeca, event) {
    event.preventDefault();

    var formulario = document.getElementById('meu-formulario-' + idPeca);
    var formData = new FormData(formulario);

    var xhr = new XMLHttpRequest();
    xhr.open('PUT', '/adicinar_item_peca_combo', true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                try {
                    var resposta = JSON.parse(xhr.responseText);
                    if (resposta.success) {
                        var message = resposta.message;
                        var cor = resposta.cor
                        var DivFlutante = document.createElement('div');
                        DivFlutante.innerHTML = `
                           <div id="DivFlutante">
                                <div class="${cor} DivFlutanteCabeça">
                                    <h3>AVISO!!!</h3>
                                    <span onclick="ButunDivFlutante()" class="close-btn">&times;</span>
                                </div>
                                <div class="DivFlutanteConte">
                                    <p>${message}</p>
                                </div>
                            </div>
                        `;
                        document.body.appendChild(DivFlutante);
                    } else {
                        alert("Erro ao adicionar peca: " + resposta.message);
                    }
                } catch (e) {
                    console.error("Erro ao analisar a resposta JSON:", e);
                    alert("Erro ao processar a resposta do servidor.");
                }
            } else {
                alert("Erro ao processar a solicitação. Tente novamente.");
            }
        }
    };

    xhr.send(formData);
}

//Adicionar Mão de obra ao Combo sem atulizar a pagina
function enviarFormularioMDOCombo(idMDO, event) {
    event.preventDefault();

    var formulario = document.getElementById('meu-formulario-' + idMDO);
    var formData = new FormData(formulario);

    var xhr = new XMLHttpRequest();
    xhr.open('PUT', '/adicinar_item_MaoObra_Combo', true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                try {
                    var resposta = JSON.parse(xhr.responseText);
                    if (resposta.success) {
                        var message = resposta.message;
                        var cor = resposta.cor
                        var DivFlutante = document.createElement('div');
                        DivFlutante.innerHTML = `
                           <div id="DivFlutante">
                                <div class="${cor} DivFlutanteCabeça">
                                    <h3>AVISO!!!</h3>
                                    <span onclick="ButunDivFlutante()" class="close-btn">&times;</span>
                                </div>
                                <div class="DivFlutanteConte">
                                    <p>${message}</p>
                                </div>
                            </div>
                        `;
                        document.body.appendChild(DivFlutante);
                    } else {
                        alert("Erro ao adicionar Mão de obra: " + resposta.message);
                    }
                } catch (e) {
                    console.error("Erro ao analisar a resposta JSON:", e);
                    alert("Erro ao processar a resposta do servidor.");
                }
            } else {
                alert("Erro ao processar a solicitação. Tente novamente.");
            }
        }
    };

    xhr.send(formData);
}

//atulizar quantidade no Combo
function atualizarItem(inputElement) {
    var novo_valor_un = $(inputElement).val();
    var item_id = $(inputElement).data("item-id");
    var Combo_id = $("#Com_id").val();
    $.ajax({
        url: "/atualizar_uni_pecas_combo/" + Combo_id + "/" + item_id,
        method: "PUT",
        data: { un: novo_valor_un },
        error: function () {
            console.log("Erro ao atualizar o item");
        }
    });
}

//atulizar lado no Combo
function atualizarLadoPecasCombo(selectElement) {
    var novo_valor_lado = $(selectElement).val();
    var item_id = $(selectElement).data("item-id");
    var Combo_id = $("#Com_id").val();
    $.ajax({
        url: "/atualizar_lado_pecas_combo/" + Combo_id + "/" + item_id,
        method: "PUT",
        data: { lado: novo_valor_lado },
        error: function () {
            console.log("Erro ao atualizar o item");
        }
    });
}

//Adicionar Carro no multiplo select2
$(document).ready(function () {
    $('#add-button-combo').on('click', function (event) {

        event.preventDefault();
        var option1 = $('#marcaT').val();
        var option2 = $('#modeloT').val();
        var option3 = $('#anoIniT').val();
        var option4 = $('#anoFinT').val();
        var option5 = $('#motorT').val();

        // Substitua "TODOS" por uma string vazia ("")
        option1 = option1 === 'TODOS' ? '' : option1;
        option2 = option2 === 'TODOS' ? '' : option2;
        option3 = option3 === 'TODOS' ? '' : option3;
        option4 = option4 === 'TODOS' ? '' : option4;
        option5 = option5 === 'TODOS' ? '' : option5;
        if (option1 === '' && option2 === '' && option3 === '' && option4 === '' && option5 === '') {
            return;
        }
        var newOptionValue = option1 + ' ' + option2 + ' ' + option3 + ' ' + option4 + ' ' + option5;

        var currentValue = $('#carrosInput').val();
        if (currentValue.indexOf(newOptionValue) === -1) {
            var newValue = currentValue ? currentValue + '\n' + newOptionValue : newOptionValue;
            $('#carrosInput').val(newValue);
        }

        var Com_id = $("#Com_id").val();
        var campos = ["nome", "status", "data_inicil_combo", "data_final_combo", "obs", "carrosInput"];
        var formData = new FormData();
        campos.forEach(function (campo) {
            formData.append(campo, $("#" + campo).val());
        });
        var fileInput = document.getElementById('image_1');
        var file = fileInput.files[0];
        formData.append('image_1', file);


        $.ajax({
            url: "/dadosCombo/" + Com_id,
            method: "PUT",
            data: formData,
            contentType: false,
            processData: false,
            error: function () {
                console.log("Erro ao atualizar o item");
            }
        });
    });
});



//Função do menu para mobile 
menuButton.addEventListener('change', toggleMenu);

function toggleMenu() {
    if (menuButton.checked) {
        menu.classList.add('active');
        content.classList.add('no-click');
    } else {
        closeMenu();
    }
}
function toggleSubMenu(option) {
    var submenu = option.nextElementSibling;
    var isActive = submenu.classList.contains('active');
    var activeSubmenus = document.getElementsByClassName('submenu active');

    for (var i = 0; i < activeSubmenus.length; i++) {
        activeSubmenus[i].classList.remove('active');
    }

    if (!isActive) {
        submenu.classList.add('active');
    }
}

function closeMenu() {
    menu.classList.remove('active');
    content.classList.remove('no-click');
    menuButton.checked = false;
}

//Função para File de imagens Para aparecer dentro do HTML quando escolhida 
function openFileInput(index) {
    const fileInput = document.getElementById(`image_${index}`);
    fileInput.click();
}

function previewImage(event, index) {
    const file = event.target.files[0];
    const reader = new FileReader();
    const previewImage = document.getElementById(`preview-image-${index}`);

    reader.onload = function (e) {
        previewImage.src = e.target.result;
    };

    reader.onerror = function (e) {
        console.error('Erro loading imagem', e);
    };

    if (file) {
        reader.readAsDataURL(file);
    }
}

//Formatador de numeros Valores expecificados nos id's
window.addEventListener('DOMContentLoaded', function () {
    var fields = [
        { id: 'telefone', format: '(XX) XXXXX-XXXX', maxLength: 11 },
        { id: 'telefone1', format: '(XX) XXXXX-XXXX', maxLength: 11 },
        { id: 'cpf', format: 'XXX.XXX.XXX-XX', maxLength: 11 },
        { id: 'cnpj', format: 'XX.XXX.XXX/XXXX-XX', maxLength: 14 },
        { id: 'niver', format: 'XX/XX/XXXX', maxLength: 8 },
        { id: 'cep', format: 'XXXXX-XXX', maxLength: 8 },
        { id: 'rg', format: 'XXXXXXXXXXXXXXX', maxLength: 15 },
        { id: 'nufor', format: 'XXXXXXXX', maxLength: 8 }
    ];

    fields.forEach(function (field) {
        var input = document.getElementById(field.id);
        var format = field.format;
        var maxLength = field.maxLength;

        if (input) {
            input.addEventListener('input', function () {
                formatInput(input, format, maxLength);
            });
        }
    });

    function formatInput(input, format, maxLength) {
        var value = input.value.replace(/\D/g, '').substr(0, maxLength);
        var formattedValue = '';

        for (var i = 0, j = 0; i < format.length; i++) {
            if (j >= value.length) {
                break;
            }

            if (format[i] === 'X') {
                formattedValue += value[j];
                j++;
            } else {
                formattedValue += format[i];
            }
        }

        input.value = formattedValue;
    }
});

//Formatador de placa EX: AAA-9999 ou AAA-9A99
document.addEventListener("DOMContentLoaded", function () {
    const inputPlaca = document.getElementById("placa");

    if (inputPlaca) {
        inputPlaca.addEventListener("keyup", function () {
            var placa = inputPlaca.value.toUpperCase();
            validarPLACA(placa);
        });
    }

    function validarPLACA(placa) {
        if (!inputPlaca) {
            return; // Retorna se o elemento não estiver presente na página
        }

        placa = placa.replace(/[^A-Z0-9]/g, "");

        if (placa.length <= 3) {
            placa = placa.replace(/[^A-Z]/g, "");
        } else if (placa.length > 3) {
            placa = placa.replace(/[^A-Z0-9]/g, "");
            placa = placa.substring(0, 3) + "-" + placa.substring(3);
        }

        inputPlaca.value = placa; // Atualiza o valor do campo de entrada
        inputPlaca.setAttribute("maxlength", 8);
    }
});


//formatador de moeda R$ 9,99 REAIS
const currencyInputs = document.querySelectorAll(".inputReais");

currencyInputs.forEach(inputElement => {
    inputElement.style.textAlign = "right";

    inputElement.addEventListener("click", function () {
        inputElement.setSelectionRange(inputElement.value.length, inputElement.value.length);
    });

    inputElement.addEventListener("input", function (event) {
        const onlyDigits = inputElement.value.replace(/\D/g, "").padStart(3, "0");
        const digitsFloat = onlyDigits.slice(0, -2) + "." + onlyDigits.slice(-2);
        const formattedValue = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(digitsFloat);
        inputElement.value = inputElement.value === "" ? "R$ 0,00" : formattedValue;
    });
});

// Espandir linha de tabela para mobile 
window.addEventListener('DOMContentLoaded', () => {
    const rows = document.querySelectorAll('.mobile-table tbody tr');

    rows.forEach(row => {
        row.addEventListener('click', () => {
            const detailsRow = row.nextElementSibling;
            const visibleRows = document.querySelectorAll('.row-details.visible');

            visibleRows.forEach(visibleRow => {
                if (visibleRow !== detailsRow) {
                    visibleRow.classList.remove('visible');
                }
            });

            detailsRow?.classList.toggle('visible');
        });

        const contentElements = row.querySelectorAll('.row-details *');
        contentElements.forEach(element => {
            element.addEventListener('click', event => {
                event.stopPropagation();
            });
        });
    });
});

//Função para estilizar e mudar o cadastro de cliente de CPF para PJ
const moveCheckbox = document.getElementById("moveCheckbox");
const labelTelefone = document.querySelector('label[for="fone"]');
const inputTelefone = document.getElementById("telefone");
const labelTelefone1 = document.querySelector('label[for="fone1"]');
const inputTelefone1 = document.getElementById("telefone1");
const labelEmail = document.querySelector('label[for="email"]');
const inputEmail = document.getElementById("email");
const cadastroPj = document.getElementById("cadastroPj");
const cadastroPj1 = document.getElementById("cadastroPj1");
const pjestilo = document.getElementById("pjestilo");
const cpfestilo = document.getElementById("cpfestilo");


const input = document.getElementById("razaoSocial");
const input1 = document.getElementById("nomeFantasia");
const input2 = document.getElementById("cnpj");

const input3 = document.getElementById("nome");

function moveInputField() {

    const isChecked = moveCheckbox.checked;
    cpfestilo.style.backgroundColor = isChecked ? "white" : "rgb(222, 221, 220)";
    pjestilo.style.backgroundColor = isChecked ? "rgb(222, 221, 220)" : "white";
    input.required = isChecked;
    input1.required = isChecked;
    input2.required = isChecked;
    input3.required = isChecked ? false : input3.required;
    cadastroPj.classList.toggle("retira", !isChecked);
    cadastroPj1.classList.toggle("retira", !isChecked);

    const targetContainer = isChecked ? cadastroPj : document.getElementById("dadosMudavel");
    targetContainer.appendChild(labelTelefone);
    targetContainer.appendChild(inputTelefone);
    targetContainer.appendChild(labelTelefone1);
    targetContainer.appendChild(inputTelefone1);
    targetContainer.appendChild(labelEmail);
    targetContainer.appendChild(inputEmail);

    localStorage.setItem("checkboxState", isChecked);
}

if (moveCheckbox) {
    moveCheckbox.addEventListener("change", moveInputField);
    moveInputField();
} else {
}

// Mensagem dinamica do flask aspecto flutuante 
const DivFlutante = document.getElementById("DivFlutante");
const content1 = document.getElementById("content");
function BloquearContet() {
    content1.classList.add('no-click');
    NavAdmin.classList.add('no-click');
    DadosBaixo.classList.add('no-click');
}

if (DivFlutante) {
    BloquearContet();
} else {
}

function ButunDivFlutante() {
    var divs = document.querySelectorAll('[id=DivFlutante]');
    for (var i = 0; i < divs.length; i++) {
        divs[i].classList.add('retira');
        content.classList.remove('no-click');
        NavAdmin.classList.remove('no-click');
        DadosBaixo.classList.remove('no-click');
    }
}


//Buscador 
const searchselector = document.getElementById("searchselector");
if (searchselector) {
    searchselector.addEventListener("change", alterarFormato);
    alterarFormato();
} else {
}

function alterarFormato() {
    var searchselector = document.getElementById("searchselector").value;
    var searchinput = document.getElementById("searchinput");
    searchinput.removeEventListener("input", validarTelefone);
    searchinput.removeEventListener("input", validarCNPJ);
    searchinput.removeEventListener("input", validarCPF);
    searchinput.removeEventListener("input", validarRG);
    searchinput.removeEventListener("input", validarID);
    searchinput.removeEventListener("input", validarPLACA);
    searchinput.removeEventListener("input", validarData);

    if (searchselector === "fone") {
        searchinput.maxLength = 15;
        searchinput.addEventListener("input", validarTelefone);
    } else if (searchselector === "cnpj") {
        searchinput.maxLength = 18;
        searchinput.addEventListener("input", validarCNPJ);
    } else if (searchselector === "cpf") {
        searchinput.maxLength = 14;
        searchinput.addEventListener("input", validarCPF);
    } else if (searchselector === "rg") {
        searchinput.maxLength = 15;
        searchinput.addEventListener("input", validarRG);
    } else if (searchselector === "id") {
        searchinput.maxLength = 8;
        searchinput.addEventListener("input", validarID);
    } else if (searchselector === "placa") {
        searchinput.maxLength = 8;
        searchinput.addEventListener("input", validarPLACA);
    } else if (searchselector === "datafor") {
        searchinput.maxLength = 21;
        searchinput.addEventListener("input", validarData);
    } else {
        searchinput.maxLength = 100;
    }

}

function formatarsearchinput(regex, mask) {
    var searchinput = document.getElementById("searchinput");
    searchinput.value = searchinput.value.replace(regex, mask);
}

function validarTelefone() {
    formatarsearchinput(/\D/g, "");
    formatarsearchinput(/^(\d{2})(\d)/g, "($1) $2");
    formatarsearchinput(/(\d)(\d{4})$/, "$1-$2");
}

function validarCNPJ() {
    formatarsearchinput(/\D/g, "");
    formatarsearchinput(/^(\d{2})(\d)/, "$1.$2");
    formatarsearchinput(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
    formatarsearchinput(/\.(\d{3})(\d)/, ".$1/$2");
    formatarsearchinput(/(\d{4})(\d)/, "$1-$2");
}

function validarCPF() {
    formatarsearchinput(/\D/g, "");
    formatarsearchinput(/(\d{3})(\d)/, "$1.$2");
    formatarsearchinput(/(\d{3})(\d)/, "$1.$2");
    formatarsearchinput(/(\d{3})(\d{1,2})$/, "$1-$2");
}

function validarRG() {
    formatarsearchinput(/\D/g, "");
}

function validarID() {
    formatarsearchinput(/\D/g, "");
}


function validarPLACA() {
    var searchinput = document.getElementById("searchinput");
    searchinput.value = searchinput.value.toUpperCase();
    searchinput.value = searchinput.value.replace(/[^A-Z0-9]/, "");
    if (searchinput.value.length <= 3) {
        searchinput.value = searchinput.value.replace(/[^A-Z]/, "");
    } else if (searchinput.value.length > 3) {
        searchinput.value = searchinput.value.replace(/[^A-Z0-9]/, "");
        searchinput.value = searchinput.value.substring(0, 3) + "-" + searchinput.value.substring(3);
    }
}

function isValidDate(dateString) {
    var customMessage = document.getElementById("customMessage");

    var datePattern = /^\d{2}\/\d{2}\/\d{4}$/;

    if (!datePattern.test(dateString)) {
        customMessage.textContent = "Formato de data inválido. Use o formato: dia/mês/ano";
        return false;
    }

    var parts = dateString.split('/');
    var day = parseInt(parts[0], 10);
    var month = parseInt(parts[1], 10) - 1;
    var year = parseInt(parts[2], 10);

    var currentDate = new Date();
    var inputDate = new Date(year, month, day);

    if (month < 0 || month > 11) {
        customMessage.textContent = "Mês inválido. Use um número entre 1 e 12.";
        return false;
    }

    var daysInMonth = new Date(year, month + 1, 0).getDate();
    if (day < 1 || day > daysInMonth) {
        customMessage.textContent = "Dia inválido para o mês selecionado.";
        return false;
    }

    if (inputDate > currentDate) {
        customMessage.textContent = "A data inserida não pode ser maior do que a data atual.";
        return false;
    }

    customMessage.textContent = "";
    return true;
}

function validarData() {
    var searchinput = document.getElementById("searchinput");
    var cleanedInput = searchinput.value.replace(/\D/g, "");
    var customMessage = document.getElementById("customMessage");

    if (cleanedInput.length >= 8) {
        var part1 = cleanedInput.substring(0, 8);
        var part2 = cleanedInput.substring(7);
        var part3 = cleanedInput.substring(8);
        var part4 = cleanedInput.substring(15);

        if (part3 === "") {
            var formattedInput = part1.replace(/(\d{2})(\d{2})(\d{4})/, "$1/$2/$3");
        } if (part2.length === 1) {
            var formatar = cleanedInput.substring(0, 2) + '/' + cleanedInput.substring(2, 4) + '/' + cleanedInput.substring(4, 8);
            isValidDate(formatar);
        } if (part3) {
            formattedInput = part1.replace(/(\d{2})(\d{2})(\d{4})/, "$1/$2/$3") + " - " + part3.replace(/(\d{2})(\d{2})(\d{4})/, "$1/$2/$3");
        } if (part4) {
            var formatar2 = cleanedInput.substring(8, 10) + '/' + cleanedInput.substring(10, 12) + '/' + cleanedInput.substring(12, 16);
            isValidDate(formatar2);
            var inputDate1 = new Date(cleanedInput.substring(4, 8), cleanedInput.substring(2, 4), cleanedInput.substring(0, 2));
            var inputDate2 = new Date(cleanedInput.substring(12, 16), cleanedInput.substring(10, 12), cleanedInput.substring(8, 10),);
            if (inputDate1 > inputDate2) {
                customMessage.textContent = "A 2° data não pode ser menor que a 1°.";
            }
        }
        searchinput.value = formattedInput;
    } else {
        searchinput.value = cleanedInput;
    }
}


//Validador antes de APAGAR
var parametro;
var produtoId;
var produtoNome;

function showDiv(param, id, nome) {
    var div = document.getElementById('DivDelet');
    div.style.display = 'block';
    content.classList.add('no-click');
    NavAdmin.classList.add('no-click');
    DadosBaixo.classList.add('no-click');
    parametro = param;
    produtoId = id;
    produtoNome = nome;
    generateRandomNumbers();
}

function hideDiv() {
    var div = document.getElementById('DivDelet');
    div.style.display = 'none';
    content.classList.remove('no-click');
    NavAdmin.classList.remove('no-click');
    DadosBaixo.classList.remove('no-click');

}

function generateRandomNumbers() {
    var randomNumbers = [];
    var min = 1000;
    var max = 9999;

    while (randomNumbers.length < 1) {
        var randomNumber = Math.floor(Math.random() * (max - min + 1)) + min;
        if (randomNumbers.indexOf(randomNumber) === -1) {
            randomNumbers.push(randomNumber);
        }
    }

    var randomNumbersElement = document.getElementById('randomNumbers');
    var randomNome = document.getElementById('retornoNome');
    randomNumbersElement.textContent = randomNumbers.join(', ');
    randomNome.textContent = produtoNome;
}

function checkNumbers() {
    var userNumbers = document.getElementById('userNumbers').value;
    var result = document.getElementById('result');

    // Verifica se o campo está vazio
    if (userNumbers === '') {
        result.textContent = 'Por favor, digite os números aleatórios.';
        return;
    }

    // Verifica se os números digitados correspondem aos números gerados
    var randomNumbers = document.getElementById('randomNumbers').textContent;
    if (userNumbers === randomNumbers) {
        var url = '/delete' + parametro + '/' + produtoId;
        console.log(url);
        axios.post(url)
            .then((response) => {
                setTimeout(function () {
                    location.reload();
                }, 100);
            })
            .catch((error) => {
                console.error(error);
            });

    } else {
        result.textContent = 'Números aleatórios incorretos! Ação não executada.';
    }
}


//Organizar Data antes de mostrar
var elementosData = document.querySelectorAll(".dataFormatada");

elementosData.forEach(function (elemento) {
    var dataOriginal = elemento.textContent;
    var dataObj = new Date(dataOriginal);

    var dia = dataObj.getDate();
    var mes = dataObj.getMonth() + 1;
    var ano = dataObj.getFullYear();
    var hora = dataObj.getHours();
    var minutos = dataObj.getMinutes();

    if (dia < 10) dia = "0" + dia;
    if (mes < 10) mes = "0" + mes;
    if (hora < 10) hora = "0" + hora;
    if (minutos < 10) minutos = "0" + minutos;

    var dataFormatada = dia + "/" + mes + "/" + ano + " " + hora + ":" + minutos;
    elemento.textContent = dataFormatada;
});

//Espandir Os Formulatios
const toggleButtons = document.querySelectorAll('.toggleButton');

toggleButtons.forEach(button => {
    const containerDados = button.nextElementSibling;
    const arrow = button.querySelector('.arrow');

    button.addEventListener('click', () => {
        containerDados.classList.toggle('hidden');
        if (containerDados.classList.contains('hidden')) {
            arrow.innerText = '▼';
        } else {
            arrow.innerText = '▲';
        }
    });
});

//Pagina dinamicamente So funciona se a tela tiver maior de 768px
function loadDynamicContent(clienteId) {
    if (window.innerWidth > 760) {
        $.ajax({
            url: '/carDinamicos/' + clienteId,
            success: function (data) {
                $('.child-container').html(data);
            }
        });
    }
}
function loadDynamicContentUser(userId) {
    if (window.innerWidth > 760) {
        $.ajax({
            url: '/carDinamicosUsuario/' + userId,
            success: function (data) {
                $('.child-container').html(data);
            }
        });
    }
}