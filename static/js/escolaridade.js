const formEscolaridade = document.getElementById("formEscolaridade");

formEscolaridade.addEventListener("submit", (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    if (!sessionStorage.getItem("nomeTurma")) {
        window.location.href = "/nova-turma";
        return;
    }

    const escolhido = formEscolaridade.querySelector('input[name="nivel"]:checked');

    if (!escolhido) {
        mostrarAviso("Selecione um nível de escolaridade.");
        return;
    }

    sessionStorage.setItem("nivelEscolaridade", escolhido.value);
    window.location.href = "/nova-turma/origem";
});
