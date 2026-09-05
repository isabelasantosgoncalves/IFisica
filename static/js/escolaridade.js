const formEscolaridade = document.getElementById("formEscolaridade");

formEscolaridade.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const nome = sessionStorage.getItem("nome");
    const descricao = sessionStorage.getItem("descricao");

    if (!nome) {
        window.location.href = "/nova-turma";
        return;
    }

    const escolhido = formEscolaridade.querySelector('input[name="nivel"]:checked');

    if (!escolhido) {
        mostrarAviso("Selecione um nível de escolaridade.");
        return;
    }

    bloquear(formEscolaridade, true);

    try {
        await enviarJson("/api/turmas", { nome, descricao, nivel: escolhido.value });

        sessionStorage.removeItem("nome");
        sessionStorage.removeItem("descricao");

        window.location.href = "/inicio";
    } catch (erro) {
        mostrarAviso(erro.message);
        bloquear(formEscolaridade, false);
    }
});
