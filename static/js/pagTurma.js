const pagina = document.getElementById("pagina");
const idTurma = pagina.dataset.idTurma;

const listaPedidos = document.getElementById("listaPedidos");
const contadorPedidos = document.getElementById("contadorPedidos");
const listaAlunos = document.getElementById("listaAlunos");
const contadorAlunos = document.getElementById("contadorAlunos");
const listaAtividades = document.getElementById("listaAtividades");
const contadorAtividades = document.getElementById("contadorAtividades");
const formAtividade = document.getElementById("formAtividade");

let souGerente = false;

function revelarBlocosDoGerente() {
    document.querySelectorAll("[data-so-gerente]").forEach((bloco) => {
        bloco.hidden = !souGerente;
    });

    if (souGerente) return;

    document.querySelector('[data-aba="atividades"]').classList.add("ativa");
    document.getElementById("painelAtividades").hidden = false;
}
const botaoSalvarAtividade = document.getElementById("botaoSalvarAtividade");
const botaoCancelarEdicaoAtividade = document.getElementById("botaoCancelarEdicaoAtividade");

function mensagemVazia(texto) {
    const paragrafo = document.createElement("p");
    paragrafo.className = "vazio";
    paragrafo.textContent = texto;
    return paragrafo;
}

// ---------- Dados da turma ----------

async function carregarTurma() {
    try {
        const resposta = await fetch(`/api/turmas/${idTurma}`);

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (resposta.status === 404) {
            window.location.href = "/inicio";
            return;
        }

        const turma = await resposta.json();

        souGerente = Boolean(turma.souGerente);
        revelarBlocosDoGerente();

        document.getElementById("nomeTurma").textContent = turma.nome;
        document.getElementById("infoTurma").textContent = souGerente
            ? turma.nivelRotulo
            : `${turma.nivelRotulo} · sala de ${turma.nomeGerente}`;
        document.getElementById("codigoConvite").textContent =
            turma.codigoConvite || "------";
        document.getElementById("descricaoTurma").textContent =
            turma.descricao || "Sem descrição.";
    } catch {
        mostrarAviso("Não foi possível carregar os dados da sala.");
    }
}

document.getElementById("botaoCopiar").addEventListener("click", async () => {
    const codigo = document.getElementById("codigoConvite").textContent;

    try {
        await navigator.clipboard.writeText(codigo);
        mostrarAviso("Código copiado!", true);
    } catch {
        mostrarAviso("Não foi possível copiar o código.");
    }
});

// ---------- Abas ----------

document.querySelectorAll(".aba").forEach((botao) => {
    botao.addEventListener("click", () => {
        document.querySelectorAll(".aba").forEach((b) => b.classList.remove("ativa"));
        botao.classList.add("ativa");

        const aba = botao.dataset.aba;
        document.getElementById("painelAlunos").hidden = aba !== "alunos";
        document.getElementById("painelAtividades").hidden = aba !== "atividades";
        document.getElementById("painelMateriais").hidden = aba !== "materiais";
        document.getElementById("painelRanking").hidden = aba !== "ranking";

        if (aba === "materiais") carregarMateriais();
        if (aba === "ranking") carregarRanking();
    });
});

// ---------- Pedidos de entrada ----------

function montarPedido(pedido) {
    const item = document.createElement("li");
    item.className = "cartao";

    const nome = document.createElement("strong");
    nome.textContent = pedido.nome;

    const email = document.createElement("span");
    email.className = "email";
    email.textContent = pedido.email;

    const decisao = document.createElement("div");
    decisao.className = "decisao";

    const aprovar = document.createElement("button");
    aprovar.type = "button";
    aprovar.className = "aprovar";
    aprovar.textContent = "Aprovar";
    aprovar.addEventListener("click", () => decidirEntrada(pedido.idSolicitacaoEntrada, true));

    const recusar = document.createElement("button");
    recusar.type = "button";
    recusar.className = "recusar";
    recusar.textContent = "Recusar";
    recusar.addEventListener("click", () => decidirEntrada(pedido.idSolicitacaoEntrada, false));

    decisao.append(aprovar, recusar);
    item.append(nome, email, decisao);
    return item;
}

async function decidirEntrada(idSolicitacaoEntrada, aprovar) {
    mostrarAviso("");

    try {
        await enviarJson(
            `/api/solicitacoes-entrada/${idSolicitacaoEntrada}`,
            { aprovar },
            "PUT"
        );

        await carregarPedidos();
        await carregarAlunos();
    } catch (erro) {
        mostrarAviso(erro.message);
    }
}

async function carregarPedidos() {
    try {
        const resposta = await fetch(`/api/turmas/${idTurma}/solicitacoes-entrada`);
        const pedidos = (await resposta.json()).filter((p) => p.status === 0);

        contadorPedidos.textContent = pedidos.length;
        contadorPedidos.classList.toggle("tem-pendencia", pedidos.length > 0);

        if (!pedidos.length) {
            listaPedidos.replaceChildren(mensagemVazia("Nenhum pedido pendente."));
            return;
        }

        listaPedidos.replaceChildren(...pedidos.map(montarPedido));
    } catch {
        listaPedidos.replaceChildren(mensagemVazia("Não foi possível carregar os pedidos."));
    }
}

// ---------- Alunos participantes ----------

function montarAluno(aluno) {
    const item = document.createElement("li");
    item.className = "cartao";

    const nome = document.createElement("strong");
    nome.textContent = aluno.nome;

    const email = document.createElement("span");
    email.className = "email";
    email.textContent = aluno.email;

    item.append(nome, email);
    return item;
}

async function carregarAlunos() {
    try {
        const resposta = await fetch(`/api/turmas/${idTurma}/participantes`);
        const alunos = await resposta.json();

        contadorAlunos.textContent = alunos.length;

        if (!alunos.length) {
            listaAlunos.replaceChildren(mensagemVazia("Ainda não há alunos nesta sala."));
            return;
        }

        listaAlunos.replaceChildren(...alunos.map(montarAluno));
    } catch {
        listaAlunos.replaceChildren(mensagemVazia("Não foi possível carregar os alunos."));
    }
}

// ---------- Atividades ----------

let atividadeEditando = null;

function montarAtividade(atividade) {
    const item = document.createElement("li");
    item.className = "cartao";

    const nome = document.createElement("strong");
    nome.textContent = atividade.nome;

    const detalhe = document.createElement("span");
    detalhe.className = "detalhe";
    detalhe.textContent = `${atividade.quantidadeQuestoes} questão(ões)`;

    const acoes = document.createElement("div");
    acoes.className = "acoes";

    const editar = document.createElement("button");
    editar.type = "button";
    editar.className = "editar";
    editar.textContent = "Editar";
    editar.addEventListener("click", () => iniciarEdicaoAtividade(atividade.idAtividade));

    const excluir = document.createElement("button");
    excluir.type = "button";
    excluir.className = "excluir-item";
    excluir.textContent = "Excluir";
    excluir.addEventListener("click", () => excluirAtividade(atividade.idAtividade));

    if (souGerente) {
        acoes.append(editar, excluir);
        item.append(nome, detalhe, acoes);
    } else {
        const link = document.createElement("a");
        link.className = "botao-responder";
        link.href = `/turma/${idTurma}/atividades/${atividade.idAtividade}`;
        link.textContent = "Responder";
        item.append(nome, detalhe, link);
    }
    return item;
}

async function carregarAtividades() {
    try {
        const resposta = await fetch(`/api/turmas/${idTurma}/atividades`);
        const atividades = await resposta.json();

        contadorAtividades.textContent = atividades.length;

        if (!atividades.length) {
            listaAtividades.replaceChildren(mensagemVazia("Nenhuma atividade criada ainda."));
            return;
        }

        listaAtividades.replaceChildren(...atividades.map(montarAtividade));
    } catch {
        listaAtividades.replaceChildren(mensagemVazia("Não foi possível carregar as atividades."));
    }
}

async function iniciarEdicaoAtividade(idAtividade) {
    mostrarAviso("");

    try {
        const resposta = await fetch(`/api/turmas/${idTurma}/atividades/${idAtividade}`);

        if (!resposta.ok) {
            const erro = await resposta.json().catch(() => ({}));
            mostrarAviso(erro.erro || "Não foi possível carregar a atividade.");
            return;
        }

        const atividade = await resposta.json();

        atividadeEditando = idAtividade;
        document.getElementById("nomeAtividade").value = atividade.nome;
        document.getElementById("descricaoAtividade").value = atividade.descricao || "";

        selecionados.clear();
        atividade.exercicios.forEach((exercicio) => selecionados.add(exercicio.idExercicio));
        contadorSelecionadas.textContent = selecionados.size;

        botaoSalvarAtividade.value = "Salvar alterações";
        botaoCancelarEdicaoAtividade.hidden = false;

        await carregarExercicios();
        formAtividade.scrollIntoView({ behavior: "smooth", block: "center" });
    } catch {
        mostrarAviso("Não foi possível carregar a atividade.");
    }
}

function cancelarEdicaoAtividade() {
    atividadeEditando = null;
    formAtividade.reset();
    selecionados.clear();
    contadorSelecionadas.textContent = "0";
    botaoSalvarAtividade.value = "Criar atividade";
    botaoCancelarEdicaoAtividade.hidden = true;
    carregarExercicios();
}

botaoCancelarEdicaoAtividade.addEventListener("click", cancelarEdicaoAtividade);

async function excluirAtividade(idAtividade) {
    if (!confirm("Excluir esta atividade? Essa ação não pode ser desfeita.")) return;

    mostrarAviso("");

    try {
        await enviarJson(`/api/turmas/${idTurma}/atividades/${idAtividade}`, null, "DELETE");

        if (atividadeEditando === idAtividade) cancelarEdicaoAtividade();

        mostrarAviso("Atividade excluída.", true);
        await carregarAtividades();
    } catch (erro) {
        mostrarAviso(erro.message);
    }
}

// ---------- Banco de questões ----------

const listaExercicios = document.getElementById("listaExercicios");
const contadorExercicios = document.getElementById("contadorExercicios");
const filtroMateria = document.getElementById("filtroMateria");
const contadorSelecionadas = document.getElementById("contadorSelecionadas");
const formQuestao = document.getElementById("formQuestao");
const campoImagem = document.getElementById("imagemQuestao");
const previaImagem = document.getElementById("previaImagem");
const imagemAtual = document.getElementById("imagemAtual");
const botaoRemoverImagem = document.getElementById("botaoRemoverImagem");

let imagemDaQuestao = null;

function mostrarPrevia(nomeArquivo) {
    imagemDaQuestao = nomeArquivo || null;

    if (!previaImagem) return;

    if (!imagemDaQuestao) {
        previaImagem.hidden = true;
        imagemAtual.removeAttribute("src");
        return;
    }

    imagemAtual.src = `/static/uploads/exercicios/${imagemDaQuestao}`;
    previaImagem.hidden = false;
}

if (botaoRemoverImagem) {
    botaoRemoverImagem.addEventListener("click", () => {
        if (campoImagem) campoImagem.value = "";
        mostrarPrevia(null);
    });
}

async function enviarImagemSelecionada() {
    if (!campoImagem || !campoImagem.files.length) return imagemDaQuestao;

    const corpo = new FormData();
    corpo.append("imagem", campoImagem.files[0]);

    const resposta = await fetch("/api/uploads/exercicios", {
        method: "POST",
        body: corpo
    });

    const dados = await resposta.json().catch(() => ({}));

    if (!resposta.ok) {
        throw new Error(dados.erro || "Não foi possível enviar a imagem.");
    }

    campoImagem.value = "";
    mostrarPrevia(dados.imagem);
    return dados.imagem;
}
const botaoSalvarQuestao = document.getElementById("botaoSalvarQuestao");
const botaoCancelarEdicaoQuestao = document.getElementById("botaoCancelarEdicaoQuestao");

const selecionados = new Set();
let exercicioEditando = null;

function montarExercicio(exercicio) {
    const item = document.createElement("li");
    item.className = "cartao";
    item.dataset.id = exercicio.idExercicio;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = selecionados.has(exercicio.idExercicio);

    const texto = document.createElement("div");

    const pergunta = document.createElement("strong");
    pergunta.textContent = exercicio.pergunta;

    const detalhe = document.createElement("span");
    detalhe.className = "detalhe";
    detalhe.textContent = `${exercicio.materia} · ${exercicio.dificuldade}`;

    const acoes = document.createElement("div");
    acoes.className = "acoes";

    const editar = document.createElement("button");
    editar.type = "button";
    editar.className = "editar";
    editar.textContent = "Editar";
    editar.addEventListener("click", (evento) => {
        evento.stopPropagation();
        iniciarEdicaoQuestao(exercicio);
    });

    const excluir = document.createElement("button");
    excluir.type = "button";
    excluir.className = "excluir-item";
    excluir.textContent = "Excluir";
    excluir.addEventListener("click", (evento) => {
        evento.stopPropagation();
        excluirQuestao(exercicio.idExercicio);
    });

    acoes.append(editar, excluir);
    texto.append(pergunta, detalhe, acoes);
    item.append(checkbox, texto);

    function alternar() {
        if (selecionados.has(exercicio.idExercicio)) {
            selecionados.delete(exercicio.idExercicio);
        } else {
            selecionados.add(exercicio.idExercicio);
        }
        checkbox.checked = selecionados.has(exercicio.idExercicio);
        item.classList.toggle("selecionada", checkbox.checked);
        contadorSelecionadas.textContent = selecionados.size;
    }

    item.classList.toggle("selecionada", checkbox.checked);
    item.addEventListener("click", (evento) => {
        if (evento.target !== checkbox) alternar();
    });
    checkbox.addEventListener("click", (evento) => {
        evento.stopPropagation();
        alternar();
    });

    return item;
}

async function carregarExercicios() {
    try {
        const materia = filtroMateria.value;
        const url = materia
            ? `/api/exercicios?materia=${encodeURIComponent(materia)}`
            : "/api/exercicios";

        const resposta = await fetch(url);
        const exercicios = await resposta.json();

        contadorExercicios.textContent = exercicios.length;

        if (!exercicios.length) {
            listaExercicios.replaceChildren(mensagemVazia("Nenhuma questão cadastrada ainda."));
            return;
        }

        listaExercicios.replaceChildren(...exercicios.map(montarExercicio));
    } catch {
        listaExercicios.replaceChildren(mensagemVazia("Não foi possível carregar as questões."));
    }
}

filtroMateria.addEventListener("change", carregarExercicios);

function iniciarEdicaoQuestao(exercicio) {
    exercicioEditando = exercicio.idExercicio;

    document.getElementById("perguntaQuestao").value = exercicio.pergunta;
    document.getElementById("materiaQuestao").value = exercicio.materia;
    document.getElementById("dificuldadeQuestao").value = exercicio.dificuldade;
    document.getElementById("alternativaA").value = exercicio.alternativaA || "";
    document.getElementById("alternativaB").value = exercicio.alternativaB || "";
    document.getElementById("alternativaC").value = exercicio.alternativaC || "";
    document.getElementById("alternativaD").value = exercicio.alternativaD || "";

    const campoResolucao = document.getElementById("resolucaoQuestao");
    if (campoResolucao) campoResolucao.value = exercicio.resolucao || "";
    mostrarPrevia(exercicio.imagem);

    const radioCerta = formQuestao.querySelector(
        `input[name="respostaCerta"][value="${exercicio.alternativaCerta}"]`
    );
    if (radioCerta) radioCerta.checked = true;

    botaoSalvarQuestao.value = "Salvar alterações";
    botaoCancelarEdicaoQuestao.hidden = false;

    formQuestao.scrollIntoView({ behavior: "smooth", block: "center" });
}

function cancelarEdicaoQuestao() {
    mostrarPrevia(null);
    exercicioEditando = null;
    formQuestao.reset();
    botaoSalvarQuestao.value = "Adicionar questão";
    botaoCancelarEdicaoQuestao.hidden = true;
}

botaoCancelarEdicaoQuestao.addEventListener("click", cancelarEdicaoQuestao);

async function excluirQuestao(idExercicio) {
    if (!confirm("Excluir esta questão? Se ela já estiver em uma atividade, a exclusão será bloqueada.")) return;

    mostrarAviso("");

    try {
        await enviarJson(`/api/exercicios/${idExercicio}`, null, "DELETE");

        selecionados.delete(idExercicio);
        contadorSelecionadas.textContent = selecionados.size;
        if (exercicioEditando === idExercicio) cancelarEdicaoQuestao();

        mostrarAviso("Questão excluída.", true);
        await carregarExercicios();
    } catch (erro) {
        mostrarAviso(erro.message);
    }
}

formQuestao.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const respostaCerta = formQuestao.querySelector('input[name="respostaCerta"]:checked');

    if (!respostaCerta) {
        mostrarAviso("Marque qual alternativa é a correta.");
        return;
    }

    const campoResolucao = document.getElementById("resolucaoQuestao");

    const corpo = {
        pergunta: document.getElementById("perguntaQuestao").value.trim(),
        materia: document.getElementById("materiaQuestao").value,
        dificuldade: document.getElementById("dificuldadeQuestao").value,
        alternativaA: document.getElementById("alternativaA").value.trim(),
        alternativaB: document.getElementById("alternativaB").value.trim(),
        alternativaC: document.getElementById("alternativaC").value.trim(),
        alternativaD: document.getElementById("alternativaD").value.trim(),
        alternativaCerta: respostaCerta.value,
        resolucao: campoResolucao ? campoResolucao.value.trim() : "",
        imagem: imagemDaQuestao
    };

    bloquear(formQuestao, true);

    try {
        corpo.imagem = await enviarImagemSelecionada();
        if (exercicioEditando) {
            await enviarJson(`/api/exercicios/${exercicioEditando}`, corpo, "PUT");
            mostrarAviso("Questão atualizada!", true);
            cancelarEdicaoQuestao();
        } else {
            await enviarJson("/api/exercicios", corpo);
            formQuestao.reset();
            mostrarPrevia(null);
            mostrarAviso("Questão criada!", true);
        }

        await carregarExercicios();
    } catch (erro) {
        mostrarAviso(erro.message);
    } finally {
        bloquear(formQuestao, false);
    }
});

// ---------- Criar/editar atividade (com base na seleção acima) ----------

formAtividade.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const nome = document.getElementById("nomeAtividade").value.trim();
    const descricao = document.getElementById("descricaoAtividade").value.trim();
    const exercicios = [...selecionados];

    if (!nome) {
        mostrarAviso("Dê um nome para a atividade.");
        return;
    }

    if (!exercicios.length) {
        mostrarAviso("Selecione pelo menos uma questão do banco acima.");
        return;
    }

    bloquear(formAtividade, true);

    try {
        if (atividadeEditando) {
            await enviarJson(
                `/api/turmas/${idTurma}/atividades/${atividadeEditando}`,
                { nome, descricao, exercicios },
                "PUT"
            );
            mostrarAviso("Atividade atualizada!", true);
            cancelarEdicaoAtividade();
        } else {
            await enviarJson(`/api/turmas/${idTurma}/atividades`, {
                nome,
                descricao,
                exercicios
            });
            formAtividade.reset();
            selecionados.clear();
            contadorSelecionadas.textContent = "0";
            mostrarAviso("Atividade criada com sucesso!", true);
        }

        await carregarAtividades();
        await carregarExercicios();
    } catch (erro) {
        mostrarAviso(erro.message);
    } finally {
        bloquear(formAtividade, false);
    }
});

async function iniciar() {
    await carregarTurma();
    await carregarAtividades();

    if (!souGerente) return;

    await carregarPedidos();
    await carregarAlunos();
    await carregarExercicios();
}

iniciar();
