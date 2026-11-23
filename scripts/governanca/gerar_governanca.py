#!/usr/bin/env python3
"""Gera a seção "Estrutura de gestão" (organograma de governança) do index.html e
do en.html, entre os marcadores <!-- GOVERNANCA:INICIO --> e <!-- GOVERNANCA:FIM -->.

Fonte: "Organograma ATPBR - estrutura sem nomes" (versão de 18/11/2026) e os nomes
dos colegiados usados na wiki (Governança de dados).

A página mostra o organograma em três níveis (deliberativas, consultivas, execução).
Cada instância é um cartão recolhível: fechado mostra a sigla e o nome; aberto, uma
frase sobre o que faz ("faz_pt"/"faz_en"). As cadeiras ficam guardadas aqui.

Para publicar os membros quando as indicações chegarem: preencha "membro" na
cadeira correspondente em COLEGIADOS (ou em EXECUTIVO) e rode
    python3 scripts/governanca/gerar_governanca.py
Enquanto nenhuma cadeira de uma instância tiver membro, o cartão não fala de
membros; assim que houver ao menos um, aparece "ver membros", que abre a lista
com os nomes e as cadeiras.
"""
import html
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def c(pt, en, membro=None, secundaria=False):
    """Uma cadeira. secundaria=True: sem voto (observador, secretaria, membro leigo)."""
    return {'pt': pt, 'en': en, 'membro': membro, 'secundaria': secundaria}


# papel: 'decide' (deliberativo) ou 'aconselha' (consultivo)
COLEGIADOS = [
    {
        'id': 'cgn',
        'faz_pt': 'Estratégia, políticas, adesão de centros e resolução de conflitos.',
        'faz_en': 'Strategy, policies, admission of centers and conflict resolution.', 'sigla': 'CGN', 'papel': 'decide', 'topo': True,
        'pt': 'Conselho de Governança Nacional',
        'en': 'National Governance Council',
        'meta_pt': ['9 com voto + 2 observadores', 'trimestral', 'instância máxima'],
        'meta_en': ['9 voting + 2 observers', 'quarterly', 'highest body'],
        'cadeiras': [
            c('Coordenação geral do ATPBR', 'ATPBR general coordination'),
            c('Presidência (direção de pesquisa do INCA)', 'Chair (INCA research directorate)'),
            c('Centro parceiro do Norte', 'Partner center in the North'),
            c('Centro parceiro do Sul', 'Partner center in the South'),
            c('Genômica clínica e diagnóstico molecular', 'Clinical genomics and molecular diagnostics'),
            c('Genômica e bioinformática do câncer', 'Cancer genomics and bioinformatics'),
            c('Oncologia clínica no SUS', 'Clinical oncology in the SUS'),
            c('Ética, direito e direitos do paciente', "Ethics, law and patients' rights"),
            c('Oncologia clínica nacional (SBOC)', 'National clinical oncology (SBOC)'),
            c('Observadores: Decit/MS e CNPq', 'Observers: Decit/MS and CNPq', secundaria=True),
        ],
    },
    {
        'id': 'ccp',
        'faz_pt': 'Avalia propostas, define prioridades, embargos, autoria e publicações.',
        'faz_en': 'Reviews proposals and sets priorities, embargoes, authorship and publications.', 'sigla': 'CCP', 'papel': 'decide',
        'pt': 'Comitê Científico e de Publicações',
        'en': 'Scientific and Publications Committee',
        'meta_pt': ['9 membros', 'mensal'],
        'meta_en': ['9 members', 'monthly'],
        'cadeiras': [
            c('Presidência · oncologia translacional', 'Chair · translational oncology'),
            c('Genômica do câncer e ancestralidade', 'Cancer genomics and ancestry'),
            c('Bioestatística', 'Biostatistics'),
            c('Epigenética e oncologia molecular', 'Epigenetics and molecular oncology'),
            c('Oncogenética e câncer hereditário', 'Oncogenetics and hereditary cancer'),
            c('Carcinogênese molecular', 'Molecular carcinogenesis'),
            c('Centro contribuinte do Nordeste', 'Contributing center in the Northeast'),
            c('Ciência de dados e dados do SUS', 'Data science and SUS data'),
            c('Genômica de tumores e oncologia cirúrgica', 'Tumor genomics and surgical oncology'),
        ],
    },
    {
        'id': 'cad',
        'faz_pt': 'Delibera pedidos de acesso controlado e acompanha os usos autorizados.',
        'faz_en': 'Decides on controlled access requests and monitors authorized uses.', 'sigla': 'CAD', 'papel': 'decide',
        'pt': 'Comitê de Acesso a Dados',
        'en': 'Data Access Committee',
        'meta_pt': ['7 membros', 'mensal'],
        'meta_en': ['7 members', 'monthly'],
        'cadeiras': [
            c('Bioética (CEP/Conep)', 'Bioethics (CEP/Conep)'),
            c('Jurídico / LGPD', 'Legal / LGPD'),
            c('Articulação com o BNT e dados clínicos', 'Liaison with the BNT and clinical data'),
            c('Genômica e infraestrutura computacional', 'Genomics and computing infrastructure'),
            c('Governança institucional do INCA', 'INCA institutional governance'),
            c('Oncologia translacional (Nordeste)', 'Translational oncology (Northeast)'),
            c('Membro leigo · indicado pelo CESP', 'Lay member · nominated by the CESP', secundaria=True),
            c('Secretaria: Núcleo Executivo', 'Secretariat: Executive Office', secundaria=True),
        ],
    },
    {
        'id': 'cesp',
        'faz_pt': 'Perspectiva de pacientes, proteção de grupos e riscos coletivos.',
        'faz_en': 'Patient perspective, protection of groups and collective risks.', 'sigla': 'CESP', 'papel': 'aconselha',
        'pt': 'Comitê de Ética, Sociedade e Participação',
        'en': 'Ethics, Society and Participation Committee',
        'meta_pt': ['5 a 7 membros', 'semestral'],
        'meta_en': ['5 to 7 members', 'twice a year'],
        'cadeiras': [
            c('Bioética', 'Bioethics'),
            c('Antropologia / raça e genética', 'Anthropology / race and genetics'),
            c('Associação de pacientes oncológicos', 'Cancer patient association'),
            c('Sociedade civil de outra região', 'Civil society from another region'),
            c('Direito / direitos humanos', 'Law / human rights'),
            c('Povos indígenas e quilombolas', 'Indigenous and quilombola peoples'),
        ],
    },
    {
        'id': 'sab',
        'faz_pt': 'Padrões internacionais, interoperabilidade e aconselhamento científico.',
        'faz_en': 'International standards, interoperability and scientific advice.', 'sigla': 'SAB', 'papel': 'aconselha',
        'pt': 'Conselho Consultivo Científico Internacional',
        'en': 'International Scientific Advisory Board',
        'meta_pt': ['5 membros', 'anual'],
        'meta_en': ['5 members', 'annual'],
        'cadeiras': [
            c('Epidemiologia internacional do câncer', 'International cancer epidemiology'),
            c('Bioinformática e genômica populacional', 'Bioinformatics and population genomics'),
            c('Direito, ética e privacidade genômica', 'Law, ethics and genomic privacy'),
            c('Bioinformática e IA em genômica nacional', 'Bioinformatics and AI in national genomics'),
            c('Biologia molecular do câncer (América Latina)', 'Cancer molecular biology (Latin America)'),
        ],
    },
]

EXECUTIVO = {
    'id': 'nucleo',
        'faz_pt': 'Recebe, valida, processa e cura os dados, apoia os centros e secretaria os colegiados.',
        'faz_en': 'Receives, validates, processes and curates the data, supports the centers and acts as secretariat to the boards.', 'sigla': 'LBBC/INCA',
    'pt': 'Núcleo Executivo e Curadoria Operacional',
    'en': 'Executive Office and Operational Curation',
    'meta_pt': ['equipe interna do INCA', 'executa e reporta ao CGN'],
    'meta_en': ['INCA internal team', 'carries out and reports to the CGN'],
    'cadeiras': [
        c('Coordenação geral', 'General coordination'),
        c('Vice-coordenação', 'Deputy coordination'),
        c('Bioinformática e pipelines', 'Bioinformatics and pipelines'),
        c('Infraestrutura e HPC', 'Infrastructure and HPC'),
        c('Curadoria e operação no HPC', 'Curation and HPC operations'),
        c('Desenvolvimento da plataforma (2 vagas)', 'Platform development (2 positions)'),
    ],
}

T = {
    'pt': {
        'kicker': 'Governança',
        'h2': 'Estrutura de gestão',
        'lede': 'O INCA coordena e mantém a plataforma. As decisões sobre ciência, acesso aos dados e ética '
                'são de colegiados em que os centros participantes têm assento e voto.',
        'consorcio': 'Consórcio ATPBR · INCA e instituições participantes',
        'niveis': {'decide': ('Deliberativas', 'Tomam decisões'),
                   'aconselha': ('Consultivas', 'Apoio transversal, sem voto'),
                   'executa': ('Execução', 'Suporte, sem voto')},
        'dica': 'Abra cada instância para ler o que ela faz.',
        'ver': 'ver membros',
        'wiki': 'Como funciona a governança',
        'wiki_href': './wiki/governanca-de-dados.html#quem-e-quem',
    },
    'en': {
        'kicker': 'Governance',
        'h2': 'Management structure',
        'lede': 'INCA coordinates and maintains the platform. Decisions on science, data access and ethics '
                'are made by boards in which the participating centers have a seat and a vote.',
        'consorcio': 'ATPBR Consortium · INCA and participating institutions',
        'niveis': {'decide': ('Decision-making', 'Take decisions'),
                   'aconselha': ('Advisory', 'Cross-cutting support, no vote'),
                   'executa': ('Execution', 'Support, no vote')},
        'dica': 'Open each body to read what it does.',
        'ver': 'see members',
        'wiki': 'How governance works',
        'wiki_href': './wiki/en/data-governance.html#who-s-who',
    },
}

e = html.escape


def membros(col, lang):
    t = T[lang]
    com = [cd for cd in col['cadeiras'] if cd['membro']]
    if not com:
        return ''
    lis = ''.join(f'<li><strong>{e(cd["membro"])}</strong> {e(cd[lang])}</li>' for cd in com)
    return f'<details class="gov-membros"><summary>{t["ver"]}</summary><ul>{lis}</ul></details>'


def cartao(col, lang, extra=''):
    """Cartão recolhível (<details>): fechado mostra só a sigla e o nome; aberto, a frase
    sobre o que a instância faz (e os membros, quando houver)."""
    nucleo = col['id'] == 'nucleo'
    sigla = '' if nucleo else f'<span class="gov-sigla" aria-hidden="true">{e(col["sigla"])}</span>'
    nome = e(col[lang]) + (f' <span class="gov-sufixo">· {e(col["sigla"])}</span>' if nucleo else '')
    return (f'<details class="gov-card gov-card-{col["id"]}{extra}">'
            f'<summary>{sigla}<h3 id="gov-{col["id"]}-{lang}">{nome}</h3>'
            f'<span class="gov-seta" aria-hidden="true"></span></summary>'
            f'<div class="gov-corpo"><p class="gov-faz">{e(col["faz_" + lang])}</p>'
            f'{membros(col, lang)}</div></details>')


def nivel(papel, conteudo, lang):
    titulo, sub = T[lang]['niveis'][papel]
    return (f'<div class="gov-nivel gov-{papel}">'
            f'<p class="gov-rotulo"><strong>{titulo}</strong> <span>{sub}</span></p>'
            f'<div class="gov-blocos">{conteudo}</div></div>')


def secao(lang):
    t = T[lang]
    por_id = {c['id']: c for c in COLEGIADOS}
    # Deliberativas: o CGN no topo, ligado ao CCP e ao CAD logo abaixo
    decide = (cartao(por_id['cgn'], lang, ' gov-topo')
              + '<div class="gov-conector" aria-hidden="true"></div>'
              + '<div class="gov-par">' + cartao(por_id['ccp'], lang) + cartao(por_id['cad'], lang) + '</div>')
    aconselha = '<div class="gov-par">' + ''.join(
        cartao(c, lang) for c in COLEGIADOS if c['papel'] == 'aconselha') + '</div>'
    executa = cartao(EXECUTIVO, lang)
    return f'''<section class="gov-section dobra" id="governanca" aria-labelledby="gov-h2">
        <div class="gov-inner">
            <div class="gov-header">
                <div>
                    <span class="kicker">{t['kicker']}</span>
                    <h2 id="gov-h2">{t['h2']}</h2>
                </div>
                <div class="gov-intro">
                    <p>{t['lede']}</p>
                    <a class="gov-link" href="{t['wiki_href']}">{t['wiki']} →</a>
                </div>
            </div>
            <div class="gov-org">
                <p class="gov-consorcio">{t['consorcio']}</p>
                {nivel('decide', decide, lang)}
                {nivel('aconselha', aconselha, lang)}
                {nivel('executa', executa, lang)}
                <p class="gov-dica">{t['dica']}</p>
            </div>
        </div>
    </section>'''


if __name__ == '__main__':
    for fn, lang in (('index.html', 'pt'), ('en.html', 'en')):
        p = os.path.join(ROOT, fn)
        s = open(p, encoding='utf-8').read()
        new, k = re.subn(r'<!-- GOVERNANCA:INICIO[^>]*-->.*?<!-- GOVERNANCA:FIM -->',
                         lambda m: '<!-- GOVERNANCA:INICIO (gerado por scripts/governanca/gerar_governanca.py; '
                         'não editar à mão) -->\n    ' + secao(lang) + '\n    <!-- GOVERNANCA:FIM -->',
                         s, flags=re.S)
        if k != 1:
            sys.exit(f'marcadores GOVERNANCA não encontrados em {fn}')
        open(p, 'w', encoding='utf-8').write(new)
    total = sum(len(col['cadeiras']) for col in COLEGIADOS) + len(EXECUTIVO['cadeiras'])
    preenchidas = sum(1 for col in COLEGIADOS + [EXECUTIVO] for cd in col['cadeiras'] if cd['membro'])
    print(f'governança: {len(COLEGIADOS)} colegiados + Núcleo Executivo, {preenchidas}/{total} cadeiras com membro')
