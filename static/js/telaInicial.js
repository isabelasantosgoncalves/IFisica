const botaoMenu = document.getElementById("botaoMenu");
const menu = document.getElementById("menu");

botaoMenu.addEventListener("click", (evento) => {
    evento.stopPropagation();
    menu.classList.toggle("ativo");
});

document.addEventListener("click", (evento) => {
    if (!menu.contains(evento.target) && !botaoMenu.contains(evento.target)) {
        menu.classList.remove("ativo");
    }
});

function montarItem(turma) {
    const item = document.createElement("li");

    const link = document.createElement("a");
    link.href = `/turma/${turma.idTurma}`;

    const titulo = document.createElement("strong");
    titulo.textContent = turma.nome;

    const detalhe = document.createElement("span");
    detalhe.textContent = ` — ${turma.nivelRotulo}`;

    link.append(titulo, detalhe);

    if (turma.pedidosPendentes) {
        const selo = document.createElement("span");
        selo.className = "selo-pendencia";
        selo.textContent = `${turma.pedidosPendentes} pedido(s) de entrada`;
        link.append(selo);
    }

    item.append(link);
    return item;
}

async function carregarTurmas() {
    const lista = document.getElementById("turmas");

    if (!lista) return;

    try {
        const resposta = await fetch("/api/turmas");

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        const turmas = await resposta.json();

        if (!turmas.length) {
            mostrarAviso("Você ainda não criou nenhuma turma.");
            return;
        }

        lista.replaceChildren(...turmas.map(montarItem));
    } catch {
        mostrarAviso("Não foi possível carregar suas turmas.");
    }
}

carregarTurmas();

// ---------- Salas em que participo ----------

function montarSala(turma) {
    const item = document.createElement("li");

    const link = document.createElement("a");
    link.href = `/turma/${turma.idTurma}`;

    const titulo = document.createElement("strong");
    titulo.textContent = turma.nome;

    const detalhe = document.createElement("span");
    detalhe.textContent = ` — ${turma.nivelRotulo} · ${turma.nomeGerente}`;

    link.append(titulo, detalhe);
    item.append(link);
    return item;
}

async function carregarSalas() {
    const lista = document.getElementById("salas");
    const aviso = document.getElementById("avisoSalas");

    if (!lista) return;

    try {
        const resposta = await fetch("/api/turmas/minhas-participacoes");

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        const salas = await resposta.json();

        if (!salas.length) {
            aviso.textContent = "Você ainda não entrou em nenhuma sala.";
            return;
        }

        aviso.textContent = "";
        lista.replaceChildren(...salas.map(montarSala));
    } catch {
        aviso.textContent = "Não foi possível carregar suas salas.";
    }
}

carregarSalas();

// ---------- Entrar em uma sala ----------

const formEntrarSala = document.getElementById("formEntrarSala");
const avisoEntrarSala = document.getElementById("avisoEntrarSala");

formEntrarSala.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    avisoEntrarSala.textContent = "";
    avisoEntrarSala.classList.remove("sucesso");

    const codigo = document.getElementById("codigoSala").value.trim();

    if (!codigo) {
        avisoEntrarSala.textContent = "Informe o código da sala.";
        return;
    }

    bloquear(formEntrarSala, true);

    try {
        const resultado = await enviarJson("/api/salas/entrar", { codigo });

        formEntrarSala.reset();
        avisoEntrarSala.textContent = resultado.mensagem;
        avisoEntrarSala.classList.add("sucesso");
        await carregarSalas();
    } catch (erro) {
        avisoEntrarSala.textContent = erro.message;
    } finally {
        bloquear(formEntrarSala, false);
    }
});
