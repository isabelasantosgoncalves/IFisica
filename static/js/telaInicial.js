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

    const titulo = document.createElement("strong");
    titulo.textContent = turma.nome;

    const detalhe = document.createElement("span");
    detalhe.textContent = ` — ${turma.nivelRotulo}`;

    item.append(titulo, detalhe);
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
