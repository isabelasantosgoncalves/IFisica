const formOrigem = document.getElementById("formOrigem");

formOrigem.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const nomeTurma = sessionStorage.getItem("nomeTurma");
    const nivelEscolaridade = sessionStorage.getItem("nivelEscolaridade");

    if (!nomeTurma) {
        window.location.href = "/nova-turma";
        return;
    }

    const escolhido = formOrigem.querySelector('input[name="origem"]:checked');

    if (!escolhido) {
        mostrarAviso("Selecione uma opção.");
        return;
    }

    bloquear(formOrigem, true);

    try {
        await enviarJson("/turmas", { nomeTurma, nivelEscolaridade });
        await enviarJson("/api/origem", { origem: escolhido.value });

        sessionStorage.removeItem("nomeTurma");
        sessionStorage.removeItem("nivelEscolaridade");

        window.location.href = "/inicio";
    } catch (erro) {
        mostrarAviso(erro.message);
        bloquear(formOrigem, false);
    }
});
