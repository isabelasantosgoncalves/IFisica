const formCadastro = document.getElementById("formCadastro");

formCadastro.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const dados = Object.fromEntries(new FormData(formCadastro));

    if (!dados.nome || !dados.email || !dados.senha) {
        mostrarAviso("Preencha nome, e-mail e senha.");
        return;
    }

    bloquear(formCadastro, true);

    try {
        await enviarJson("/api/docentes", dados);
        window.location.href = "/inicio";
    } catch (erro) {
        mostrarAviso(erro.message);
        bloquear(formCadastro, false);
    }
});
