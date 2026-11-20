# -*- coding: utf-8 -*-
"""Gera a seção "Uma rede nacional" (mapa interativo + lista) e a injeta em
index.html e en.html, entre os marcadores <!-- REDE:INICIO --> e <!-- REDE:FIM -->.

Fonte dos dados: centros.py (a mesma lista usada na brochura do ATPBR).
Uso:  python3 scripts/rede/gerar_rede.py   (a partir da raiz do repositório)
"""
import json, math, os, re, sys, collections, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from centros import CITIES, INST, REGION  # noqa: E402

GEO = json.load(open(os.path.join(HERE, 'br_simplificado.json')))

K = math.cos(math.radians(14))
def prj(lon, lat): return (lon * K, -lat)
pts = [prj(*c) for f in GEO for ring in f['rings'] for c in ring]
xmin = min(p[0] for p in pts); xmax = max(p[0] for p in pts)
ymin = min(p[1] for p in pts); ymax = max(p[1] for p in pts)
W = 1000; S = W / (xmax - xmin); H = (ymax - ymin) * S
def P(lon, lat):
    x, y = prj(lon, lat); return ((x - xmin) * S, (y - ymin) * S)

REG_EN = {'Norte': 'North', 'Nordeste': 'Northeast', 'Sudeste': 'Southeast', 'Sul': 'South', 'Centro-Oeste': 'Central-West'}
REG_ORDER = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
REG_KEY = {'Norte': 'norte', 'Nordeste': 'nordeste', 'Centro-Oeste': 'centro-oeste', 'Sudeste': 'sudeste', 'Sul': 'sul'}
UF_REG = {f['uf']: REGION.get(f['uf']) for f in GEO}
# estados sem centro também precisam de região (só para a cor)
UF_REG.update({'AC': 'Norte', 'AP': 'Norte', 'TO': 'Norte', 'RR': 'Norte', 'AL': 'Nordeste', 'SE': 'Nordeste',
               'PI': 'Nordeste', 'MT': 'Centro-Oeste', 'GO': 'Centro-Oeste'})

by_city = collections.defaultdict(list)
for nome, cidade, _chk in INST:
    by_city[cidade].append(nome)
n_inst = len(INST); n_cid = len(by_city); n_uf = len({CITIES[c][0] for c in by_city})

LAB = {'São Paulo': (24, 6, 'start'), 'Rio de Janeiro': (24, 18, 'start'), 'Porto Alegre': (-24, 10, 'end'),
       'Recife': (22, 8, 'start'), 'Belém': (-20, -14, 'end'), 'Belo Horizonte': (22, -6, 'start'),
       'Brasília': (20, -14, 'start'), 'Salvador': (20, 8, 'start'), 'Manaus': (0, -22, 'middle'),
       'Fortaleza': (20, -12, 'start'), 'Curitiba': (-22, 8, 'end'), 'Boa Vista': (16, -12, 'start'),
       'Porto Velho': (-16, 22, 'end')}

def esc(s): return html.escape(s, quote=True)

def svg(lang):
    out = [f'<svg class="rede-svg" viewBox="-10 -10 {W+110:.0f} {H+20:.0f}" role="img" '
           f'aria-labelledby="rede-svg-title"><title id="rede-svg-title">'
           + ('Mapa do Brasil com as cidades que têm instituições da rede ATPBR' if lang == 'pt'
              else 'Map of Brazil showing the cities with ATPBR network institutions') + '</title>']
    for f in GEO:
        d = ''
        for ring in f['rings']:
            q = [P(*c) for c in ring]
            d += 'M' + 'L'.join(f'{a:.0f},{b:.0f}' for a, b in q) + 'Z'
        reg = REG_KEY[UF_REG[f['uf']]]
        out.append(f'<path class="uf" data-regiao="{reg}" d="{d}"/>')
    items = sorted(by_city, key=lambda c: -len(by_city[c]))
    for c in items:
        x, y = P(CITIES[c][1], CITIES[c][2]); n = len(by_city[c])
        r = 7 + 6.5 * math.sqrt(n - 1)
        uf = CITIES[c][0]; reg = REG_KEY[REGION[uf]]
        lbl = (f'{c} ({uf}): {n} ' + ('instituições' if n > 1 else 'instituição')) if lang == 'pt' else \
              (f'{c} ({uf}): {n} institution' + ('s' if n > 1 else ''))
        out.append(f'<g class="cidade" tabindex="0" role="button" data-cidade="{esc(c)}" data-regiao="{reg}" '
                   f'aria-label="{esc(lbl)}" style="--d:{(y/H):.2f}">'
                   f'<circle class="halo" cx="{x:.0f}" cy="{y:.0f}" r="{r+8:.0f}"/>'
                   f'<circle class="ponto" cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}"/>'
                   + (f'<text class="n" x="{x:.0f}" y="{y+5.5:.0f}">{n}</text>' if n > 1 else '') + '</g>')
    for c in items:
        if c not in LAB: continue
        x, y = P(CITIES[c][1], CITIES[c][2]); dx, dy, an = LAB[c]
        out.append(f'<text class="rot" x="{x+dx:.0f}" y="{y+dy:.0f}" text-anchor="{an}">{esc(c)}</text>')
    out.append('</svg>')
    return ''.join(out)

def lista(lang):
    parts = []
    for reg in REG_ORDER:
        cities = sorted([c for c in by_city if REGION[CITIES[c][0]] == reg], key=lambda c: (CITIES[c][0], c))
        if not cities: continue
        n = sum(len(by_city[c]) for c in cities)
        nome = reg if lang == 'pt' else REG_EN[reg]
        parts.append(f'<details class="rede-reg" data-regiao="{REG_KEY[reg]}"><summary><span>{nome}</span>'
                     f'<span class="rede-reg-n">{n}</span></summary><ul>')
        for c in cities:
            insts = ''.join(f'<li>{esc(i)}</li>' for i in sorted(by_city[c]))
            parts.append(f'<li class="rede-cid" data-cidade="{esc(c)}"><b>{esc(c)} · {CITIES[c][0]}</b><ul>{insts}</ul></li>')
        parts.append('</ul></details>')
    return ''.join(parts)

T = {
 'pt': dict(kicker='Rede ATPBR', h2='Uma rede nacional',
            lede='Hospitais, universidades e centros de pesquisa de todas as regiões do país geram e compartilham os dados que formam o Atlas.',
            inst='instituições', cid='cidades', uf='estados', reg='regiões',
            hint='Toque ou passe o mouse sobre uma cidade para ver as instituições.',
            todas='Todas', lista='Lista completa por região', nota='Rede em formação: a lista é atualizada à medida que novas instituições aderem ao consórcio. Dados de novembro de 2026.'),
 'en': dict(kicker='ATPBR network', h2='A nationwide network',
            lede='Hospitals, universities and research centres from every region of the country generate and share the data that make up the Atlas.',
            inst='institutions', cid='cities', uf='states', reg='regions',
            hint='Tap or hover over a city to see its institutions.',
            todas='All', lista='Full list by region', nota='A growing network: the list is updated as new institutions join the consortium. Data as of November 2026.'),
}

def secao(lang):
    t = T[lang]
    chips = f'<button type="button" class="rede-chip ativo" data-filtro="">{t["todas"]}</button>' + ''.join(
        f'<button type="button" class="rede-chip" data-filtro="{REG_KEY[r]}">{r if lang=="pt" else REG_EN[r]}</button>' for r in REG_ORDER)
    dados = json.dumps({c: {'uf': CITIES[c][0], 'inst': sorted(v)} for c, v in by_city.items()}, ensure_ascii=False)
    return f'''<section class="rede-section" id="rede" aria-labelledby="rede-h2">
        <div class="rede-inner">
            <div class="rede-texto">
                <span class="kicker">{t['kicker']}</span>
                <h2 id="rede-h2">{t['h2']}</h2>
                <p class="rede-lede">{t['lede']}</p>
                <dl class="rede-nums">
                    <div><dt>{t['inst']}</dt><dd>60+</dd></div>
                    <div><dt>{t['cid']}</dt><dd>{n_cid}</dd></div>
                    <div><dt>{t['uf']}</dt><dd>{n_uf}</dd></div>
                    <div><dt>{t['reg']}</dt><dd>5</dd></div>
                </dl>
                <div class="rede-chips" role="group" aria-label="{t['reg']}">{chips}</div>
                <div class="rede-painel" id="redePainel" aria-live="polite">
                    <p class="rede-hint">{t['hint']}</p>
                </div>
            </div>
            <div class="rede-mapa">{svg(lang)}</div>
        </div>
        <div class="rede-lista">
            <h3>{t['lista']}</h3>
            <div class="rede-lista-grid">{lista(lang)}</div>
            <p class="rede-nota">{t['nota']}</p>
        </div>
        <script type="application/json" id="redeDados">{dados}</script>
    </section>'''

for fn, lang in (('index.html', 'pt'), ('en.html', 'en')):
    p = os.path.join(ROOT, fn); s = open(p, encoding='utf-8').read()
    new, k = re.subn(r'<!-- REDE:INICIO[^>]*-->.*?<!-- REDE:FIM -->',
                     lambda m: '<!-- REDE:INICIO (gerado por scripts/rede/gerar_rede.py; não editar à mão) -->\n    '
                     + secao(lang) + '\n    <!-- REDE:FIM -->', s, flags=re.S)
    if k != 1: sys.exit(f'marcadores não encontrados em {fn}')
    open(p, 'w', encoding='utf-8').write(new)
print(n_inst, 'instituições,', n_cid, 'cidades,', n_uf, 'UFs')
