# -*- coding: utf-8 -*-
"""Gera br_simplificado.json (contornos dos estados simplificados) a partir de um GeoJSON
de UFs do Brasil (o br.json usado na brochura). Uso: python3 simplificar_geo.py br.json"""
import json, sys, math, os
TOL = 0.06  # graus
def dp(pts, tol):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / L
        if d > dmax: dmax, idx = d, i
    if dmax > tol:
        return dp(pts[:idx + 1], tol)[:-1] + dp(pts[idx:], tol)
    return [pts[0], pts[-1]]
D = json.load(open(sys.argv[1]))
out = []
for f in D['features']:
    rings = []
    g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for poly in polys:
        ring = poly[0]
        h = len(ring) // 2  # anel fechado: simplifica as duas metades
        s = dp(ring[:h + 1], TOL)[:-1] + dp(ring[h:], TOL)
        if len(s) >= 4: rings.append([[round(x, 3), round(y, 3)] for x, y in s])
    out.append({'uf': f['properties']['sigla'], 'rings': rings})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'br_simplificado.json'), 'w'), separators=(',', ':'))
print(sum(len(r) for f in out for r in f['rings']), 'pontos')
