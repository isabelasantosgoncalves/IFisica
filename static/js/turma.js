const formTurma = document.getElementById("formTurma");

formTurma.addEventListener("submit", (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const nome = document.getElementById("nomeTurma").value.trim();
    const descricao = document.getElementById("descricao").value.trim();

    if (!nome) {
        mostrarAviso("Dê um nome para a turma.");
        return;
    }

    sessionStorage.setItem("nome", nome);
    sessionStorage.setItem("descricao", descricao);
    window.location.href = "/nova-turma/escolaridade";
});
