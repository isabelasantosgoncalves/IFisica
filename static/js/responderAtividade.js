const pagina = document.getElementById("pagina");
const idTurma = pagina.dataset.idTurma;
const idAtividade = pagina.dataset.idAtividade;

const nomeAtividade = document.getElementById("nomeAtividade");
const descricaoAtividade = document.getElementById("descricaoAtividade");
const painelResultado = document.getElementById("painelResultado");
const textoResultado = document.getElementById("textoResultado");
const formResponder = document.getElementById("formResponder");
const listaQuestoes = document.getElementById("listaQuestoes");
const listaCorrecao = document.getElementById("listaCorrecao");

const LETRAS = ["A", "B", "C", "D"];

function montarImagem(idArquivo) {
    if (!idArquivo) return null;

    const imagem = document.createElement("img");
    imagem.className = "imagem-questao";
    imagem.src = `/api/arquivos/${idArquivo}`;
    imagem.alt = "Imagem da questão";
    imagem.loading = "lazy";
    return imagem;
}

function montarCorrecao(questao, indice) {
    const item = document.createElement("li");
    item.className = questao.correta ? "correcao acertou" : "correcao errou";

    const marca = document.createElement("span");
    marca.className = "marca";
    marca.textContent = questao.correta ? "Acertou" : "Errou";

    const enunciado = document.createElement("p");
    enunciado.className = "enunciado";
    enunciado.textContent = `${indice + 1}. ${questao.pergunta}`;

    item.append(marca, enunciado);

    const imagem = montarImagem(questao.idImagem);
    if (imagem) item.append(imagem);

    for (const letra of LETRAS) {
        const texto = questao[`alternativa${letra}`];
        if (!texto) continue;

        const linha = document.createElement("p");
        linha.className = "alternativa";

        if (letra === questao.alternativaCerta) linha.classList.add("certa");
        if (letra === questao.respostaDada) linha.classList.add("marcada");

        let sufixo = "";
        if (letra === questao.respostaDada && letra === questao.alternativaCerta) {
            sufixo = "  ← sua resposta, correta";
        } else if (letra === questao.respostaDada) {
            sufixo = "  ← sua resposta";
        } else if (letra === questao.alternativaCerta) {
            sufixo = "  ← resposta correta";
        }

        linha.textContent = `${letra}) ${texto}${sufixo}`;
        item.append(linha);
    }

    if (questao.resolucao) {
        const titulo = document.createElement("p");
        titulo.className = "titulo-resolucao";
        titulo.textContent = "Resolução";

        const resolucao = document.createElement("p");
        resolucao.className = "resolucao";
        resolucao.textContent = questao.resolucao;

        item.append(titulo, resolucao);
    }

    return item;
}

function mostrarResultado(texto, detalhes) {
    formResponder.hidden = true;
    painelResultado.hidden = false;
    textoResultado.textContent = texto;

    if (!listaCorrecao) return;

    if (!detalhes || !detalhes.length) {
        listaCorrecao.replaceChildren();
        return;
    }

    listaCorrecao.replaceChildren(...detalhes.map(montarCorrecao));
}

function montarQuestao(questao, indice) {
    const item = document.createElement("li");
    item.className = "questao";

    const enunciado = document.createElement("span");
    enunciado.className = "enunciado";
    enunciado.textContent = `${indice + 1}. ${questao.pergunta}`;

    const tags = document.createElement("span");
    tags.className = "tags";
    tags.textContent = `${questao.materia} · ${questao.dificuldade}`;

    item.append(enunciado, tags);

    const imagem = montarImagem(questao.idImagem);
    if (imagem) item.append(imagem);

    const alternativas = [
        ["A", questao.alternativaA],
        ["B", questao.alternativaB],
        ["C", questao.alternativaC],
        ["D", questao.alternativaD]
    ];

    for (const [letra, texto] of alternativas) {
        if (!texto) continue;

        const linha = document.createElement("label");
        linha.className = "alternativa";

        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = `questao-${questao.idExercicio}`;
        radio.value = letra;
        radio.required = true;

        linha.append(radio, document.createTextNode(`${letra}) ${texto}`));
        item.append(linha);
    }

    return item;
}

async function carregar() {
    try {
        const resposta = await fetch(`/api/turmas/${idTurma}/atividades/${idAtividade}/questoes`);

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (resposta.status === 403 || resposta.status === 404) {
            const erro = await resposta.json().catch(() => ({}));
            mostrarAviso(erro.erro || "Não foi possível abrir esta atividade.");
            return;
        }

        const dados = await resposta.json();

        if (dados.atividade) {
            nomeAtividade.textContent = dados.atividade.nome;
            descricaoAtividade.textContent = dados.atividade.descricao || "";
        } else {
            nomeAtividade.textContent = "Atividade";
        }

        if (dados.jaRespondida) {
            mostrarResultado(
                `Você já respondeu esta atividade. Acertos: ${dados.pontuacao} de ${dados.total}.`,
                dados.detalhes
            );
            return;
        }

        if (!dados.questoes.length) {
            listaQuestoes.replaceChildren(mensagemVazia("Esta atividade ainda não tem questões."));
            formResponder.hidden = false;
            return;
        }

        listaQuestoes.replaceChildren(
            ...dados.questoes.map((questao, indice) => montarQuestao(questao, indice))
        );
        formResponder.hidden = false;
    } catch {
        mostrarAviso("Não foi possível carregar a atividade.");
    }
}

function mensagemVazia(texto) {
    const paragrafo = document.createElement("p");
    paragrafo.className = "vazio";
    paragrafo.textContent = texto;
    return paragrafo;
}

formResponder.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const respostas = {};
    let faltando = false;

    listaQuestoes.querySelectorAll(".questao").forEach((item, indice) => {
        const nomeGrupo = [...item.querySelectorAll("input[type=radio]")][0]?.name;
        if (!nomeGrupo) return;

        const marcada = item.querySelector(`input[name="${nomeGrupo}"]:checked`);
        if (!marcada) {
            faltando = true;
            return;
        }

        const idExercicio = nomeGrupo.replace("questao-", "");
        respostas[idExercicio] = marcada.value;
    });

    if (faltando) {
        mostrarAviso("Responda todas as questões antes de enviar.");
        return;
    }

    bloquear(formResponder, true);

    try {
        const resultado = await enviarJson(
            `/api/turmas/${idTurma}/atividades/${idAtividade}/respostas`,
            { respostas }
        );

        mostrarResultado(
            `Respostas enviadas! Acertos: ${resultado.acertos} de ${resultado.total}.`,
            resultado.detalhes
        );
    } catch (erro) {
        mostrarAviso(erro.message);
    } finally {
        bloquear(formResponder, false);
    }
});

carregar();
