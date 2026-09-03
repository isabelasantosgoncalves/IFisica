async function enviarJson(url, corpo, metodo = "POST") {
    const resposta = await fetch(url, {
        method: metodo,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(corpo)
    });

    const dados = await resposta.json().catch(() => ({}));

    if (!resposta.ok) {
        throw new Error(dados.erro || "Não foi possível concluir a operação.");
    }

    return dados;
}

function mostrarAviso(texto, sucesso = false) {
    const aviso = document.getElementById("aviso");
    if (!aviso) return;
    aviso.textContent = texto;
    aviso.classList.toggle("sucesso", sucesso);
}

function bloquear(form, bloqueado) {
    const botao = form.querySelector('[type="submit"]');
    if (botao) botao.disabled = bloqueado;
}
