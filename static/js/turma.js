const formTurma = document.getElementById("formTurma");

formTurma.addEventListener("submit", (evento) => {
    evento.preventDefault();
    mostrarAviso("");

    const nomeTurma = document.getElementById("nomeTurma").value.trim();

    if (!nomeTurma) {
        mostrarAviso("Dê um nome para a turma.");
        return;
    }

    sessionStorage.setItem("nomeTurma", nomeTurma);
    window.location.href = "/nova-turma/escolaridade";
});
