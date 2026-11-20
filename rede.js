/* Interações adicionadas em nov/2026: mapa da rede, menu móvel e números animados. */
(function () {
    'use strict';
    var reduz = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var pt = (document.documentElement.lang || '').toLowerCase().indexOf('pt') === 0;

    /* ── Menu móvel: fecha ao escolher um link e mantém aria-expanded ── */
    var hamb = document.getElementById('headerHamburger');
    var popup = document.getElementById('headerPopup');
    if (hamb && popup) {
        new MutationObserver(function () {
            hamb.setAttribute('aria-expanded', popup.classList.contains('open') ? 'true' : 'false');
        }).observe(popup, { attributes: true, attributeFilter: ['class'] });
        popup.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', function () { if (popup.classList.contains('open')) hamb.click(); });
        });
    }

    /* ── Barras por tipo de câncer: animam quando entram na tela ── */
    var tipos = document.querySelector('.tipos-lista');
    if (tipos) {
        if (reduz || !('IntersectionObserver' in window)) tipos.classList.add('visivel');
        else new IntersectionObserver(function (es, ob) {
            es.forEach(function (e) { if (e.isIntersecting) { tipos.classList.add('visivel'); ob.disconnect(); } });
        }, { threshold: 0.25 }).observe(tipos);
    }

    /* ── Mapa da rede ── */
    var sec = document.getElementById('rede');
    if (!sec) return;
    var dados = JSON.parse(document.getElementById('redeDados').textContent);
    var painel = document.getElementById('redePainel');
    var hint = painel.innerHTML;
    var cidades = sec.querySelectorAll('.cidade');
    var fixa = null;

    // <g> do SVG não tem o método click() (só elementos HTML têm): dispara o evento
    function clica(g) { g.dispatchEvent(new MouseEvent('click')); }

    function esc(t) { var d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

    function mostra(nome) {
        var c = dados[nome];
        if (!c) { painel.innerHTML = hint; return; }
        var n = c.inst.length;
        var tit = n + (pt ? (n > 1 ? ' instituições' : ' instituição') : (n > 1 ? ' institutions' : ' institution'));
        painel.innerHTML = '<p class="rede-p-cidade">' + esc(nome) + ' <span>' + c.uf + '</span></p>' +
            '<p class="rede-p-n">' + tit + '</p><ul>' +
            c.inst.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</ul>';
        cidades.forEach(function (g) { g.classList.toggle('ativa', g.getAttribute('data-cidade') === nome); });
    }
    function limpa() {
        if (fixa) { mostra(fixa); return; }
        painel.innerHTML = hint;
        cidades.forEach(function (g) { g.classList.remove('ativa'); });
    }

    cidades.forEach(function (g) {
        var nome = g.getAttribute('data-cidade');
        g.addEventListener('mouseenter', function () { mostra(nome); });
        g.addEventListener('mouseleave', limpa);
        g.addEventListener('focus', function () { mostra(nome); });
        g.addEventListener('click', function () { fixa = (fixa === nome ? null : nome); fixa ? mostra(nome) : limpa(); });
        g.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); clica(g); }
        });
    });

    /* ── Toque no celular ──
       Num celular os pontos têm de 5 a 16 px, pequenos demais para o dedo:
       um toque no mapa escolhe a cidade mais próxima (até RAIO px da borda do
       ponto). Tocar longe de todas limpa a seleção. */
    var svgMapa = sec.querySelector('.rede-svg');
    var mapa = sec.querySelector('.rede-mapa');
    var RAIO = 28;
    var estreito = window.matchMedia('(max-width: 900px)');
    svgMapa.addEventListener('click', function (e) {
        if (!e.target.closest('.cidade')) {
            var melhor = null, dist = Infinity;
            cidades.forEach(function (g) {
                if (g.classList.contains('fora')) return;
                var r = g.querySelector('.ponto').getBoundingClientRect();
                var d = Math.hypot(e.clientX - (r.left + r.width / 2), e.clientY - (r.top + r.height / 2)) - r.width / 2;
                if (d < dist) { dist = d; melhor = g; }
            });
            if (melhor && dist <= RAIO) clica(melhor);
            else if (fixa) { fixa = null; limpa(); }
        }
        // em tela estreita o painel fica abaixo do mapa: rola até ele se não estiver visível
        if (fixa && estreito.matches) {
            var p = painel.getBoundingClientRect();
            if (p.bottom > window.innerHeight || p.top < 0) painel.scrollIntoView({ block: 'nearest', behavior: reduz ? 'auto' : 'smooth' });
        }
    });

    /* Em tela estreita (uma coluna) o painel vai para baixo do mapa, para a lista
       de instituições não empurrar o mapa para baixo do dedo a cada toque. */
    var marcaPainel = document.createComment('lugar do painel no computador');
    painel.parentNode.insertBefore(marcaPainel, painel);
    function posicionaPainel() {
        if (estreito.matches) mapa.parentNode.insertBefore(painel, mapa.nextSibling);
        else marcaPainel.parentNode.insertBefore(painel, marcaPainel.nextSibling);
        sec.classList.toggle('painel-abaixo', estreito.matches);
    }
    posicionaPainel();
    if (estreito.addEventListener) estreito.addEventListener('change', posicionaPainel);
    else if (estreito.addListener) estreito.addListener(posicionaPainel);

    /* filtro por região */
    var chips = sec.querySelectorAll('.rede-chip');
    chips.forEach(function (ch) {
        ch.addEventListener('click', function () {
            var f = ch.getAttribute('data-filtro');
            chips.forEach(function (c) { c.classList.toggle('ativo', c === ch); c.setAttribute('aria-pressed', c === ch ? 'true' : 'false'); });
            sec.classList.toggle('filtrando', !!f);
            sec.querySelectorAll('[data-regiao]').forEach(function (el) {
                el.classList.toggle('fora', !!f && el.getAttribute('data-regiao') !== f);
            });
            sec.querySelectorAll('.rede-reg').forEach(function (d) { d.open = !!f && d.getAttribute('data-regiao') === f; });
            fixa = null; limpa();
        });
    });

    /* pontos aparecem em sequência quando o mapa entra na tela */
    if (!reduz && 'IntersectionObserver' in window) {
        sec.classList.add('pre');
        new IntersectionObserver(function (es, ob) {
            es.forEach(function (e) { if (e.isIntersecting) { sec.classList.remove('pre'); sec.classList.add('entra'); ob.disconnect(); } });
        }, { threshold: 0.2 }).observe(sec.querySelector('.rede-mapa'));
    }
})();
