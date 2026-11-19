/* Wiki do ATPBR: copiado para atpbr/wiki/ por tools/build_wiki.py. Edite aqui. */
(function () {
    // ── Menu lateral no celular ──
    var side = document.getElementById('wk-side');
    var menu = document.querySelector('.wk-menu');
    if (menu && side) {
        menu.addEventListener('click', function () {
            var open = side.classList.toggle('open');
            menu.setAttribute('aria-expanded', open ? 'true' : 'false');
            if (open) document.getElementById('wk-q').focus();
        });
        side.addEventListener('click', function (e) {
            if (e.target.closest('a')) { side.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); }
        });
    }

    // ── Busca (índice gerado em search-index.js) ──
    var input = document.getElementById('wk-q');
    var results = document.getElementById('wk-results');
    var nav = document.getElementById('wk-nav');
    var pages = window.WIKI_INDEX || [];
    if (!input || !pages.length) return;

    // texto sem acentos e em minúsculas (busca "governanca" acha "governança")
    function fold(s) {
        return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    }
    pages.forEach(function (p) { p.fx = fold(p.x); p.ft = fold(p.t); });

    function esc(s) {
        return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
    }

    function snippet(p, term) {
        var i = p.fx.indexOf(term);
        if (i < 0) return esc(p.x.slice(0, 140)) + '…';
        var start = Math.max(0, i - 60), end = Math.min(p.x.length, i + term.length + 80);
        // as posições valem no texto sem acentos; mapIndex as converte para o original
        var orig = p.x, folded = p.fx;
        var a = mapIndex(orig, start), b = mapIndex(orig, i), c = mapIndex(orig, i + term.length), d = mapIndex(orig, end);
        return (start > 0 ? '…' : '') + esc(orig.slice(a, b)) + '<mark>' + esc(orig.slice(b, c)) + '</mark>' +
            esc(orig.slice(c, d)) + (end < folded.length ? '…' : '');
    }

    // posição no texto sem acentos -> posição no texto original
    function mapIndex(orig, foldedPos) {
        var count = 0;
        for (var k = 0; k < orig.length; k++) {
            if (count >= foldedPos) return k;
            count += orig[k].normalize('NFD').replace(/[̀-ͯ]/g, '').length;
        }
        return orig.length;
    }

    function search(q) {
        var terms = fold(q).split(/\s+/).filter(function (t) { return t.length > 1; });
        if (!terms.length) { results.hidden = true; nav.hidden = false; return; }
        var hits = pages.map(function (p) {
            var score = 0;
            for (var j = 0; j < terms.length; j++) {
                var t = terms[j], inTitle = p.ft.indexOf(t) >= 0, n = p.fx.split(t).length - 1;
                if (!inTitle && !n) return null;
                score += (inTitle ? 50 : 0) + Math.min(n, 20);
            }
            return { p: p, score: score };
        }).filter(Boolean).sort(function (a, b) { return b.score - a.score; });

        results.innerHTML = hits.length
            ? hits.map(function (h) {
                return '<a href="' + h.p.u + '"><strong>' + esc(h.p.t) + '</strong><span>' + snippet(h.p, terms[0]) + '</span></a>';
            }).join('')
            : '<p>' + esc(results.getAttribute('data-empty') || 'Nada encontrado para') + ' “' + esc(q) + '”.</p>';
        results.hidden = false;
        nav.hidden = true;
    }

    input.addEventListener('input', function () { search(input.value); });
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { var first = results.querySelector('a'); if (first) location.href = first.href; }
        if (e.key === 'Escape') { input.value = ''; search(''); }
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === '/' && document.activeElement !== input && !/input|textarea/i.test(document.activeElement.tagName)) {
            e.preventDefault();
            if (side && getComputedStyle(side).display === 'none' && menu) menu.click();
            input.focus();
        }
    });
})();
