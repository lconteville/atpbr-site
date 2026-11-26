/* Botões "Acessar a plataforma" (menu do topo, menu do celular e cards do
   "Participe"): todo link com o atributo data-plataforma.

   O clique abre uma janela com dois botões, Dashboard e Gestão de Dados.
   Os endereços ficam só aqui (PLATAFORMA_LINKS) e valem para o site em PT e EN;
   cada botão da janela é ligado pelo atributo data-destino. */
const PLATAFORMA_LINKS = {
    dashboard: 'https://atpbr.inca.gov.br/public-bi',
    gestao: 'https://atpbr.inca.gov.br/front',
};

(function () {
    const janela = document.getElementById('avisoPlataforma');
    if (!janela) return;

    janela.querySelectorAll('a[data-destino]').forEach((link) => {
        const url = PLATAFORMA_LINKS[link.dataset.destino];
        if (url) link.href = url;
        link.addEventListener('click', () => janela.close());
    });

    if (typeof janela.showModal !== 'function') {
        // navegador sem <dialog>: os botões vão direto para a Gestão de Dados
        document.querySelectorAll('a[data-plataforma]').forEach((botao) => {
            botao.href = PLATAFORMA_LINKS.gestao;
            botao.target = '_blank';
            botao.rel = 'noopener';
        });
        return;
    }

    document.querySelectorAll('a[data-plataforma]').forEach((botao) => {
        botao.addEventListener('click', (e) => {
            e.preventDefault();
            // fecha o menu do celular, se estiver aberto
            const popup = document.getElementById('headerPopup');
            if (popup && popup.classList.contains('open')) {
                document.getElementById('headerHamburger').click();
            }
            janela.showModal();
        });
    });

    janela.querySelectorAll('[data-fechar]').forEach((b) => b.addEventListener('click', () => janela.close()));
    // clique fora do cartão (no fundo escurecido) fecha
    janela.addEventListener('click', (e) => { if (e.target === janela) janela.close(); });
})();
