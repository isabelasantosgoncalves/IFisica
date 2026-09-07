const formSenha = document.getElementById("formSenha");

formSenha.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const atual = document.getElementById("senhaAtual").value;
    const nova = document.getElementById("senhaNova").value;
    const confirma = document.getElementById("senhaConfirma").value;

    if (!atual || !nova || !confirma) {
        mostrarAviso("Preencha os três campos.");
        return;
    }

    if (nova !== confirma) {
        mostrarAviso("A nova senha e a repetição não são iguais.");
        return;
    }

    bloquear(formSenha, true);

    try {
        const resultado = await enviarJson(
            "/api/perfil/senha",
            { senhaAtual: atual, senhaNova: nova },
            "PUT"
        );

        formSenha.reset();
        mostrarAviso(resultado.mensagem, true);
    } catch (erro) {
        mostrarAviso(erro.message);
    } finally {
        bloquear(formSenha, false);
    }
});
