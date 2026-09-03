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

async function carregarTurmas() {
    const lista = document.getElementById("turmas");

    try {
        const resposta = await fetch("/turmas");

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        const turmas = await resposta.json();

        if (!turmas.length) {
            mostrarAviso("Você ainda não criou nenhuma turma.");
            return;
        }

        lista.innerHTML = turmas
            .map((turma) => `<li>${turma.nomeTurma} — ${turma.nivelEscolaridade || "sem nível"}</li>`)
            .join("");
    } catch {
        mostrarAviso("Não foi possível carregar suas turmas.");
    }
}

carregarTurmas();
