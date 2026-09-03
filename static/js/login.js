const formLogin = document.getElementById("formLogin");

formLogin.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const dados = Object.fromEntries(new FormData(formLogin));

    if (!dados.email || !dados.senha) {
        mostrarAviso("Informe e-mail e senha.");
        return;
    }

    bloquear(formLogin, true);

    try {
        await enviarJson("/api/login", dados);
        window.location.href = "/inicio";
    } catch (erro) {
        mostrarAviso(erro.message);
        bloquear(formLogin, false);
    }
});
