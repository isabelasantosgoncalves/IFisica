const formPerfil = document.getElementById("formPerfil");
const seletorGenero = document.getElementById("genero");
const campoAutodeclaracao = document.getElementById("campoAutodeclaracao");

seletorGenero.addEventListener("change", () => {
    campoAutodeclaracao.hidden = seletorGenero.value !== "autodeclaracao";
});

function montarSala(sala, souGerente) {
    const item = document.createElement("li");

    const link = document.createElement("a");
    link.href = "/turma/" + sala.idTurma;

    const nome = document.createElement("strong");
    nome.textContent = sala.nome;

    const detalhe = document.createElement("span");
    detalhe.textContent = souGerente
        ? " — " + sala.nivelRotulo
        : " — " + sala.nivelRotulo + " · " + sala.nomeGerente;

    link.append(nome, detalhe);

    if (souGerente && sala.pedidosPendentes) {
        const selo = document.createElement("span");
        selo.className = "selo-pendencia";
        selo.textContent = sala.pedidosPendentes + " pedido(s)";
        link.append(selo);
    }

    item.append(link);
    return item;
}

function preencherSalas(lista, salas, souGerente, mensagem) {
    if (!salas.length) {
        const vazio = document.createElement("li");
        vazio.className = "vazio";
        vazio.textContent = mensagem;
        lista.replaceChildren(vazio);
        return;
    }

    lista.replaceChildren(...salas.map((s) => montarSala(s, souGerente)));
}

function mostrarNivel(progresso) {
    document.getElementById("nivelAluno").textContent = progresso.nivel;

    const partes = [
        progresso.respondidas + " questão(ões) respondida(s)",
        progresso.acertos + " acerto(s)",
        progresso.aproveitamento + "% de aproveitamento"
    ];

    if (progresso.proximoNivel) {
        partes.push(
            "faltam " + progresso.faltamParaOProximo + " para " + progresso.proximoNivel
        );
    } else {
        partes.push("nível máximo alcançado");
    }

    document.getElementById("detalheProgresso").textContent = partes.join(" · ");

    const faixa = progresso.faltamParaOProximo +
        (progresso.respondidas - progresso.minimoDoNivel);

    const avanco = faixa > 0
        ? Math.round((progresso.respondidas - progresso.minimoDoNivel) * 100 / faixa)
        : 100;

    document.getElementById("barraNivel").style.width = avanco + "%";
    document.getElementById("cartaoNivel").hidden = false;
}

async function carregar() {
    try {
        const resposta = await fetch("/api/perfil");

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!resposta.ok) {
            mostrarAviso("Não foi possível carregar seu perfil.");
            return;
        }

        const perfil = await resposta.json();

        document.getElementById("resumoPapel").textContent =
            "Você entra na plataforma como " + perfil.papel + ".";

        document.getElementById("nome").value = perfil.nome;
        document.getElementById("telefone").value = perfil.telefone;
        document.getElementById("email").textContent = perfil.email;
        document.getElementById("dataNasc").textContent = perfil.dataNasc;

        seletorGenero.value = perfil.genero || "";
        campoAutodeclaracao.hidden = perfil.genero !== "autodeclaracao";
        document.getElementById("generoAutodeclarado").value =
            perfil.generoAutodeclarado || "";

        mostrarNivel(perfil.progresso);

        const gerencia = perfil.salasQueGerencia;
        const tituloGerencia = document.getElementById("tituloGerencia");

        if (gerencia.length) {
            tituloGerencia.hidden = false;
            preencherSalas(
                document.getElementById("salasGerencia"), gerencia, true, ""
            );
        }

        preencherSalas(
            document.getElementById("salasParticipa"),
            perfil.salasQueParticipa,
            false,
            "Você ainda não entrou em nenhuma sala."
        );
    } catch {
        mostrarAviso("Não foi possível carregar seu perfil.");
    }
}

formPerfil.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const dados = Object.fromEntries(new FormData(formPerfil));

    if (!dados.nome.trim() || !dados.telefone.trim()) {
        mostrarAviso("Nome e telefone são obrigatórios.");
        return;
    }

    bloquear(formPerfil, true);

    try {
        const resultado = await enviarJson("/api/perfil", dados, "PUT");
        mostrarAviso(resultado.mensagem, true);
    } catch (erro) {
        mostrarAviso(erro.message);
    } finally {
        bloquear(formPerfil, false);
    }
});

carregar();
