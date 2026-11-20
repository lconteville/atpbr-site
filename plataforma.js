/* Botão "Acessar a plataforma" (menu do topo e menu do celular).
   Enquanto o link for o provisório (href="#"), o clique abre o aviso
   "Em breve". Quando o endereço real for colocado no href, o aviso
   deixa de aparecer e o botão leva direto à plataforma. */
(function () {
    const aviso = document.getElementById('avisoPlataforma');
    if (!aviso || typeof aviso.showModal !== 'function') return;

    const botoes = document.querySelectorAll('.header-cta-plataforma, .popup-cta-plataforma');
    botoes.forEach((botao) => {
        botao.addEventListener('click', (e) => {
            if (botao.getAttribute('href') !== '#') return; // link real: segue normalmente
            e.preventDefault();
            // fecha o menu do celular, se estiver aberto
            const popup = document.getElementById('headerPopup');
            if (popup && popup.classList.contains('open')) {
                document.getElementById('headerHamburger').click();
            }
            aviso.showModal();
        });
    });

    aviso.querySelectorAll('[data-fechar]').forEach((b) => b.addEventListener('click', () => aviso.close()));
    // clique fora do cartão (no fundo escurecido) fecha
    aviso.addEventListener('click', (e) => { if (e.target === aviso) aviso.close(); });
})();
