/* Botões "Acessar a plataforma" (menu do topo, menu do celular e cards do
   "Participe"): todo link com o atributo data-plataforma.

   >>> No dia do lançamento, preencha PLATAFORMA_URL com o endereço da
   >>> plataforma. É o único lugar a mudar, vale para o site em PT e EN.

   Enquanto PLATAFORMA_URL estiver vazio, o clique abre o aviso "Em breve".
   Quando estiver preenchido, os botões levam direto à plataforma (nova aba). */
const PLATAFORMA_URL = '';

(function () {
    const botoes = document.querySelectorAll('a[data-plataforma]');

    if (PLATAFORMA_URL) {
        botoes.forEach((botao) => {
            botao.href = PLATAFORMA_URL;
            botao.target = '_blank';
            botao.rel = 'noopener';
        });
        return;
    }

    const aviso = document.getElementById('avisoPlataforma');
    if (!aviso || typeof aviso.showModal !== 'function') return;

    botoes.forEach((botao) => {
        botao.addEventListener('click', (e) => {
            if (botao.getAttribute('href') !== '#') return; // link real no HTML: segue normalmente
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
