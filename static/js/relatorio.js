const pagina = document.getElementById("pagina");
const idTurma = pagina.dataset.idTurma;

function celula(texto, classe) {
    const td = document.createElement("td");
    td.textContent = texto;
    if (classe) td.className = classe;
    return td;
}

function corDoPercentual(percentual) {
    if (percentual === null) return "sem-dado";
    if (percentual >= 70) return "bom";
    if (percentual >= 40) return "medio";
    return "ruim";
}

function textoPercentual(percentual) {
    return percentual === null ? "—" : percentual + "%";
}

function preencher(idTabela, linhas, montarLinha, mensagemVazia) {
    const corpo = document.querySelector("#" + idTabela + " tbody");

    if (!linhas.length) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = document.querySelectorAll("#" + idTabela + " thead th").length;
        td.className = "vazio";
        td.textContent = mensagemVazia;
        tr.append(td);
        corpo.replaceChildren(tr);
        return;
    }

    corpo.replaceChildren(...linhas.map(montarLinha));
}

function montarLinhaAluno(aluno) {
    const tr = document.createElement("tr");
    tr.append(
        celula(aluno.nome),
        celula(String(aluno.atividadesFeitas)),
        celula(aluno.acertos + " de " + aluno.questoes),
        celula(aluno.aproveitamento + "%", corDoPercentual(aluno.aproveitamento))
    );
    return tr;
}

function montarLinhaAtividade(atividade) {
    const tr = document.createElement("tr");
    tr.append(
        celula(atividade.nome),
        celula(String(atividade.quemFez)),
        celula(atividade.acertos + " de " + atividade.questoes),
        celula(
            textoPercentual(atividade.mediaPercentual),
            corDoPercentual(atividade.mediaPercentual)
        )
    );
    return tr;
}

function montarLinhaQuestao(questao) {
    const tr = document.createElement("tr");
    tr.append(
        celula(questao.pergunta, "coluna-larga"),
        celula(questao.materia),
        celula(questao.dificuldade),
        celula(String(questao.respostas)),
        celula(String(questao.acertos)),
        celula(
            textoPercentual(questao.percentualAcerto),
            corDoPercentual(questao.percentualAcerto)
        )
    );
    return tr;
}

function montarDificil(questao) {
    const item = document.createElement("li");
    item.className = "questao-dificil";

    const pergunta = document.createElement("p");
    pergunta.className = "pergunta";
    pergunta.textContent = questao.pergunta;

    const numeros = document.createElement("p");
    numeros.className = "numeros";
    numeros.textContent =
        questao.percentualAcerto + "% de acerto · " +
        questao.acertos + " de " + questao.respostas + " resposta(s) · " +
        questao.materia + " · " + questao.dificuldade;

    const barra = document.createElement("div");
    barra.className = "barra";

    const preenchida = document.createElement("div");
    preenchida.className = corDoPercentual(questao.percentualAcerto);
    preenchida.style.width = questao.percentualAcerto + "%";

    barra.append(preenchida);
    item.append(pergunta, numeros, barra);
    return item;
}

async function carregar() {
    try {
        const [respostaTurma, respostaRelatorio] = await Promise.all([
            fetch("/api/turmas/" + idTurma),
            fetch("/api/turmas/" + idTurma + "/relatorio")
        ]);

        if (respostaRelatorio.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!respostaRelatorio.ok) {
            const erro = await respostaRelatorio.json().catch(() => ({}));
            mostrarAviso(erro.erro || "Não foi possível carregar o relatório.");
            return;
        }

        if (respostaTurma.ok) {
            const turma = await respostaTurma.json();
            document.getElementById("nomeTurma").textContent =
                turma.nome + " · " + turma.nivelRotulo;
        }

        const dados = await respostaRelatorio.json();
        const resumo = dados.resumo;

        document.getElementById("numAlunos").textContent = resumo.participantes;
        document.getElementById("numResponderam").textContent = resumo.responderam;
        document.getElementById("numSemResponder").textContent = resumo.semResponder;
        document.getElementById("numAtividades").textContent = resumo.atividades;
        document.getElementById("numAproveitamento").textContent =
            textoPercentual(resumo.aproveitamento);
        document.getElementById("resumo").hidden = false;

        const dificeis = document.getElementById("listaDificeis");

        if (!dados.questoesMaisDificeis.length) {
            const vazio = document.createElement("p");
            vazio.className = "vazio";
            vazio.textContent = "Ninguém respondeu questões desta sala ainda.";
            dificeis.replaceChildren(vazio);
        } else {
            dificeis.replaceChildren(...dados.questoesMaisDificeis.map(montarDificil));
        }

        preencher("tabelaAlunos", dados.porAluno, montarLinhaAluno,
            "Nenhum aluno respondeu atividades ainda.");
        preencher("tabelaAtividades", dados.porAtividade, montarLinhaAtividade,
            "Nenhuma atividade criada ainda.");
        preencher("tabelaQuestoes", dados.porQuestao, montarLinhaQuestao,
            "Nenhuma questão em atividades desta sala.");
    } catch {
        mostrarAviso("Não foi possível carregar o relatório.");
    }
}

carregar();
