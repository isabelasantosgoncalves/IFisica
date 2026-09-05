const listaPendentes = document.getElementById("listaPendentes");
const contador = document.getElementById("contador");
const detalhe = document.getElementById("detalhe");

let selecionada = null;

function campo(rotulo, valor) {
    const bloco = document.createElement("div");
    bloco.className = "campo";

    const termo = document.createElement("dt");
    termo.textContent = rotulo;

    const definicao = document.createElement("dd");
    definicao.textContent = valor || "Não informado";

    bloco.append(termo, definicao);
    return bloco;
}

function mensagemVazia(texto) {
    const paragrafo = document.createElement("p");
    paragrafo.className = "vazio";
    paragrafo.textContent = texto;
    return paragrafo;
}

function montarDetalhe(pedido) {
    const titulo = document.createElement("h3");
    titulo.textContent = pedido.nome;

    const email = document.createElement("p");
    email.className = "email";
    email.textContent = pedido.email;

    const lista = document.createElement("dl");
    lista.append(
        campo("Motivo", pedido.motivo),
        campo("Conteúdo que pretende ensinar", pedido.conteudo),
        campo("Público-alvo", pedido.publicoAlvo),
        campo("Enviada em", pedido.dataSolicitacao)
    );

    const decisao = document.createElement("div");
    decisao.className = "decisao";

    const aprovar = document.createElement("button");
    aprovar.type = "button";
    aprovar.className = "aprovar";
    aprovar.textContent = "Aprovar";
    aprovar.addEventListener("click", () => decidir(pedido.idSolicitacao, true));

    const recusar = document.createElement("button");
    recusar.type = "button";
    recusar.className = "recusar";
    recusar.textContent = "Recusar";
    recusar.addEventListener("click", () => decidir(pedido.idSolicitacao, false));

    decisao.append(aprovar, recusar);

    detalhe.replaceChildren(titulo, email, lista, decisao);
}

function montarItem(pedido) {
    const item = document.createElement("li");

    const botao = document.createElement("button");
    botao.type = "button";
    botao.setAttribute("aria-current", String(pedido.idSolicitacao === selecionada));

    const nome = document.createElement("strong");
    nome.textContent = pedido.nome;

    const email = document.createElement("span");
    email.className = "email";
    email.textContent = pedido.email;

    botao.append(nome, email);
    botao.addEventListener("click", () => {
        selecionada = pedido.idSolicitacao;
        montarDetalhe(pedido);
        marcarSelecionada();
    });

    item.append(botao);
    return item;
}

function marcarSelecionada() {
    listaPendentes.querySelectorAll("button").forEach((botao, indice) => {
        botao.setAttribute(
            "aria-current",
            String(pendentes[indice].idSolicitacao === selecionada)
        );
    });
}

let pendentes = [];

async function decidir(idSolicitacao, aprovar) {
    mostrarAviso("");

    try {
        const resultado = await enviarJson(
            `/api/solicitacoes/${idSolicitacao}`,
            { aprovar },
            "PUT"
        );

        selecionada = null;
        detalhe.replaceChildren(mensagemVazia(resultado.mensagem));
        await carregarPendentes();
    } catch (erro) {
        mostrarAviso(erro.message);
    }
}

async function carregarPendentes() {
    try {
        const resposta = await fetch("/api/solicitacoes");

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (resposta.status === 403) {
            window.location.href = "/inicio";
            return;
        }

        pendentes = await resposta.json();
        contador.textContent = pendentes.length;

        if (!pendentes.length) {
            listaPendentes.replaceChildren();
            mostrarAviso("Nenhuma solicitação aguardando análise.");
            return;
        }

        mostrarAviso("");
        listaPendentes.replaceChildren(...pendentes.map(montarItem));
    } catch {
        mostrarAviso("Não foi possível carregar as solicitações.");
    }
}

carregarPendentes();
