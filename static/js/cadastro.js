const formCadastro = document.getElementById("formCadastro");
const seletorGenero = document.getElementById("genero");
const campoAutodeclaracao = document.getElementById("campoAutodeclaracao");

seletorGenero.addEventListener("change", () => {
    campoAutodeclaracao.hidden = seletorGenero.value !== "autodeclaracao";
});

formCadastro.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const dados = Object.fromEntries(new FormData(formCadastro));

    bloquear(formCadastro, true);

    try {
        await enviarJson("/api/usuarios", dados);
        window.location.href = "/inicio";
    } catch (erro) {
        mostrarAviso(erro.message);
        bloquear(formCadastro, false);
    }
});
