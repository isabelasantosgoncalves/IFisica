// Materiais de estudo e ranking da sala.
// Roda depois de pagTurma.js e reaproveita idTurma, souGerente e mensagemVazia.

const listaMateriais = document.getElementById("listaMateriais");
const contadorMateriais = document.getElementById("contadorMateriais");
const formMaterial = document.getElementById("formMaterial");
const campoLink = document.getElementById("campoLink");
const campoPdf = document.getElementById("campoPdf");
const arquivoMaterial = document.getElementById("arquivoMaterial");
const pdfEnviado = document.getElementById("pdfEnviado");
const botaoSalvarMaterial = document.getElementById("botaoSalvarMaterial");
const botaoCancelarEdicaoMaterial = document.getElementById("botaoCancelarEdicaoMaterial");
const listaRanking = document.getElementById("listaRanking");

let materialEditando = null;
let idArquivoDoMaterial = null;

function tipoMaterialEscolhido() {
    const marcado = formMaterial.querySelector('input[name="tipoMaterial"]:checked');
    return marcado ? marcado.value : "link";
}

function alternarCamposMaterial() {
    const tipo = tipoMaterialEscolhido();
    campoLink.hidden = tipo !== "link";
    campoPdf.hidden = tipo !== "pdf";
}

formMaterial.querySelectorAll('input[name="tipoMaterial"]').forEach((radio) => {
    radio.addEventListener("change", alternarCamposMaterial);
});

function montarMaterial(material) {
    const item = document.createElement("li");
    item.className = "cartao material";

    const etiqueta = document.createElement("span");
    etiqueta.className = "etiqueta-tipo " + material.tipo;
    etiqueta.textContent = material.tipo === "pdf" ? "PDF" : "Link";

    const link = document.createElement("a");
    link.className = "titulo-material";
    link.href = material.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = material.titulo;

    item.append(etiqueta, link);

    if (material.descricao) {
        const descricao = document.createElement("p");
        descricao.className = "detalhe";
        descricao.textContent = material.descricao;
        item.append(descricao);
    }

    if (souGerente) {
        const acoes = document.createElement("div");
        acoes.className = "acoes";

        const editar = document.createElement("button");
        editar.type = "button";
        editar.className = "editar";
        editar.textContent = "Editar";
        editar.addEventListener("click", () => iniciarEdicaoMaterial(material));

        const excluir = document.createElement("button");
        excluir.type = "button";
        excluir.className = "excluir-item";
        excluir.textContent = "Excluir";
        excluir.addEventListener("click", () => excluirMaterial(material.idMaterial));

        acoes.append(editar, excluir);
        item.append(acoes);
    }

    return item;
}

function agruparPorAssunto(materiais) {
    const grupos = new Map();

    for (const material of materiais) {
        if (!grupos.has(material.assunto)) grupos.set(material.assunto, []);
        grupos.get(material.assunto).push(material);
    }

    return [...grupos.entries()].map(([assunto, itens]) => {
        const grupo = document.createElement("div");
        grupo.className = "grupo-assunto";

        const titulo = document.createElement("h4");
        titulo.textContent = assunto;

        const lista = document.createElement("ul");
        lista.className = "lista-cartoes";
        lista.replaceChildren(...itens.map(montarMaterial));

        grupo.append(titulo, lista);
        return grupo;
    });
}

async function carregarMateriais() {
    try {
        const resposta = await fetch("/api/turmas/" + idTurma + "/materiais");

        if (!resposta.ok) {
            listaMateriais.replaceChildren(
                mensagemVazia("Não foi possível carregar os materiais.")
            );
            return;
        }

        const materiais = await resposta.json();
        contadorMateriais.textContent = materiais.length;

        if (!materiais.length) {
            listaMateriais.replaceChildren(
                mensagemVazia("Nenhum material publicado ainda.")
            );
            return;
        }

        listaMateriais.replaceChildren(...agruparPorAssunto(materiais));
    } catch {
        listaMateriais.replaceChildren(
            mensagemVazia("Não foi possível carregar os materiais.")
        );
    }
}

function iniciarEdicaoMaterial(material) {
    materialEditando = material.idMaterial;
    idArquivoDoMaterial = material.idArquivo;

    document.getElementById("assuntoMaterial").value = material.assunto;
    document.getElementById("tituloMaterial").value = material.titulo;
    document.getElementById("descricaoMaterial").value = material.descricao || "";
    document.getElementById("urlMaterial").value =
        material.tipo === "link" ? material.url : "";

    formMaterial.querySelector(
        'input[name="tipoMaterial"][value="' + material.tipo + '"]'
    ).checked = true;

    alternarCamposMaterial();

    pdfEnviado.hidden = material.tipo !== "pdf";
    pdfEnviado.textContent = material.tipo === "pdf"
        ? "PDF já enviado. Escolha outro só se quiser trocar."
        : "";

    botaoSalvarMaterial.value = "Salvar alterações";
    botaoCancelarEdicaoMaterial.hidden = false;
    formMaterial.scrollIntoView({ behavior: "smooth", block: "center" });
}

function cancelarEdicaoMaterial() {
    materialEditando = null;
    idArquivoDoMaterial = null;
    formMaterial.reset();
    alternarCamposMaterial();
    pdfEnviado.hidden = true;
    botaoSalvarMaterial.value = "Adicionar material";
    botaoCancelarEdicaoMaterial.hidden = true;
}

botaoCancelarEdicaoMaterial.addEventListener("click", cancelarEdicaoMaterial);

async function excluirMaterial(idMaterial) {
    if (!confirm("Excluir este material?")) return;

    mostrarAviso("");

    try {
        await enviarJson(
            "/api/turmas/" + idTurma + "/materiais/" + idMaterial,
            null,
            "DELETE"
        );

        if (materialEditando === idMaterial) cancelarEdicaoMaterial();

        mostrarAviso("Material excluído.", true);
        await carregarMateriais();
    } catch (erro) {
        mostrarAviso(erro.message);
    }
}

async function enviarPdfSelecionado() {
    if (!arquivoMaterial.files.length) return idArquivoDoMaterial;

    const corpo = new FormData();
    corpo.append("arquivo", arquivoMaterial.files[0]);

    const resposta = await fetch("/api/uploads/materiais", {
        method: "POST",
        body: corpo
    });

    const dados = await resposta.json().catch(() => ({}));

    if (!resposta.ok) {
        throw new Error(dados.erro || "Não foi possível enviar o PDF.");
    }

    arquivoMaterial.value = "";
    return dados.idArquivo;
}

formMaterial.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const tipo = tipoMaterialEscolhido();

    const corpo = {
        assunto: document.getElementById("assuntoMaterial").value.trim(),
        titulo: document.getElementById("tituloMaterial").value.trim(),
        descricao: document.getElementById("descricaoMaterial").value.trim(),
        tipo: tipo,
        url: document.getElementById("urlMaterial").value.trim()
    };

    bloquear(formMaterial, true);

    try {
        if (tipo === "pdf") corpo.idArquivo = await enviarPdfSelecionado();

        if (materialEditando) {
            await enviarJson(
                "/api/turmas/" + idTurma + "/materiais/" + materialEditando,
                corpo,
                "PUT"
            );
            mostrarAviso("Material atualizado!", true);
            cancelarEdicaoMaterial();
        } else {
            await enviarJson("/api/turmas/" + idTurma + "/materiais", corpo);
            formMaterial.reset();
            alternarCamposMaterial();
            mostrarAviso("Material adicionado!", true);
        }

        await carregarMateriais();
    } catch (erro) {
        mostrarAviso(erro.message);
    } finally {
        bloquear(formMaterial, false);
    }
});

function montarLinhaRanking(linha) {
    const item = document.createElement("li");
    item.className = linha.souEu ? "linha-ranking eu" : "linha-ranking";

    const posicao = document.createElement("span");
    posicao.className = "posicao";
    posicao.textContent = linha.posicao + "º";

    const nome = document.createElement("span");
    nome.className = "nome";
    nome.textContent = linha.nome;

    const numeros = document.createElement("span");
    numeros.className = "numeros";
    numeros.textContent =
        linha.acertos + " de " + linha.questoes +
        " · " + linha.aproveitamento + "%" +
        " · " + linha.atividadesFeitas + " atividade(s)";

    item.append(posicao, nome, numeros);
    return item;
}

async function carregarRanking() {
    try {
        const resposta = await fetch("/api/turmas/" + idTurma + "/ranking");

        if (!resposta.ok) {
            listaRanking.replaceChildren(
                mensagemVazia("Não foi possível carregar o ranking.")
            );
            return;
        }

        const linhas = await resposta.json();

        if (!linhas.length) {
            listaRanking.replaceChildren(
                mensagemVazia("Ninguém respondeu atividades desta sala ainda.")
            );
            return;
        }

        listaRanking.replaceChildren(...linhas.map(montarLinhaRanking));
    } catch {
        listaRanking.replaceChildren(
            mensagemVazia("Não foi possível carregar o ranking.")
        );
    }
}

alternarCamposMaterial();
