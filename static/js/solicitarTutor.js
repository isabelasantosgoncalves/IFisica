const formTutoria = document.getElementById("formTutoria");
const situacao = document.getElementById("situacao");

function mostrarSituacao(texto) {
    situacao.textContent = texto;
    situacao.hidden = false;
    formTutoria.hidden = true;
}

async function carregarSituacao() {
    try {
        const resposta = await fetch("/api/solicitacoes/minha");

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        const pedido = await resposta.json();

        if (!pedido) return;

        if (pedido.status === 0) {
            mostrarSituacao(
                "Você já enviou uma solicitação e ela está aguardando análise."
            );
            return;
        }

        if (pedido.status === 1) {
            mostrarSituacao("Sua solicitação foi aprovada. Você já é tutor.");
            return;
        }

        situacao.textContent =
            "Sua solicitação anterior foi recusada. Você pode enviar outra.";
        situacao.hidden = false;
    } catch {
        mostrarAviso("Não foi possível verificar sua solicitação.");
    }
}

formTutoria.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const dados = Object.fromEntries(new FormData(formTutoria));

    if (!dados.motivo.trim() || !dados.conteudo.trim() || !dados.publicoAlvo.trim()) {
        mostrarAviso("Preencha motivo, conteúdo e público-alvo.");
        return;
    }

    bloquear(formTutoria, true);

    try {
        const resultado = await enviarJson("/api/solicitacoes", dados);
        mostrarSituacao(resultado.mensagem);
    } catch (erro) {
        mostrarAviso(erro.message);
        bloquear(formTutoria, false);
    }
});

carregarSituacao();
