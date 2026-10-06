"""Extrae las tarifas de medassure beauty (España) de la calculadora de medassurance.de.

La calculadora que incrusta medassure.es se carga desde medassurance.de y usa dos servicios:
  - settings:  lista de tratamientos con su categoría (A-F), exclusiones y preguntas de riesgo.
  - calculate: prima para una selección de tratamientos, tarifa (basic/premium) y duración.

Uso:  python3 extraer_tarifas.py tarifas_medassure_beauty_ES.json
"""
import datetime
import itertools
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

WS = 'https://medassurance.de/die/jhc/medassure/beauty/nxt/'
PRODUCT = 'jhc-medassure-beauty-es'
PLANS = ('basic', 'premium')
DURATIONS = (1, 2, 5)


def post(endpoint, body):
    req = urllib.request.Request(WS + endpoint, data=json.dumps(body).encode(), method='POST',
                                 headers={'Content-Type': 'application/json', 'Origin': 'https://medassure.es'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def settings():
    # sin "product" el servidor no responde; es el nombre que monta la web para la variante "es"
    return post('settings', {'product': {'name': PRODUCT, 'prefix': 'beauty-', 'variant': 'es', 'parameter': 'beauty-es'},
                             'productname': PRODUCT, 'country': 'es', 'suffix': '', 'ws': WS})


def calculate(treatments, plan, duration):
    start = datetime.date.today() + datetime.timedelta(days=30)
    end = start.replace(year=start.year + duration)
    ms = lambda d: int(time.mktime(d.timetuple()) * 1000)
    body = {'productname': PRODUCT, 'product': PRODUCT, 'country': 'es', 'placeofTreatment': 'es',
            'duration': duration, 'plan': plan, 'soc': ms(start), 'eoc': ms(end), 'opdate': start.strftime('%d.%m.%Y'),
            'group': False, 'tids': treatments, 'beHappy': False, 'riskQuerySelected': {}, 'height': 0, 'weight': 0}
    return post('calculate', body)['fee']


def main(out):
    st = settings()
    ts = [t for t in st['treatments'] if t['visible'] and PRODUCT in t['products']]
    by_uuid = {t['uuid']: t for t in ts}
    by_cat = {}
    for t in ts:
        by_cat.setdefault(t['cat'], []).append(t)
    cats = sorted(by_cat)

    with ThreadPoolExecutor(8) as ex:
        # precio de un tratamiento: se comprueba que todos los de una categoría cuestan lo mismo
        jobs = [(t, p, d) for t in ts for p in PLANS for d in DURATIONS]
        fees = list(ex.map(lambda j: calculate([j[0]], j[1], j[2]), jobs))
        prices = {}
        for (t, p, d), fee in zip(jobs, fees):
            cur = prices.setdefault(t['cat'], {}).setdefault(p, {}).setdefault(d, fee)
            if cur != fee:
                raise SystemExit(f'{t["name"]}: {fee} distinto de la categoría {t["cat"]} ({cur})')

        # recargo por varios tratamientos: prima - precio de la categoría más cara
        # tratamientos que se pueden combinar libremente (sin liposucciones ni balón gástrico, que tienen exclusiones)
        free = {c: [t for t in by_cat[c] if not t['exclusion']] for c in cats}
        combos = [list(c) for n in (2, 3, 4) for c in itertools.combinations([c for c in cats if free[c]], n)]
        jobs = [(c, p, d) for c in combos for p in PLANS for d in DURATIONS]
        pick = lambda c: [free[x][0] for x in c]
        fees = list(ex.map(lambda j: calculate(pick(j[0]), j[1], j[2]), jobs))
    surcharge = {}
    for (c, p, d), fee in zip(jobs, fees):
        extra = fee - max(prices[x][p][d] for x in c)
        if surcharge.setdefault(len(c), extra) != extra:
            raise SystemExit(f'recargo no uniforme para {len(c)} tratamientos: {extra} / {surcharge[len(c)]}')

    data = {
        'fuente': WS + 'settings y ' + WS + 'calculate (producto ' + PRODUCT + ')',
        'fecha_extraccion': datetime.date.today().isoformat(),
        'duraciones_anos': list(DURATIONS),
        'max_tratamientos': {'basic': 3, 'premium': 4},
        'precios': {c: {p: [prices[c][p][d] for d in DURATIONS] for p in PLANS} for c in cats},
        'recargo_por_n_tratamientos': {str(n): surcharge[n] for n in sorted(surcharge)},
        'regla': 'prima = precio de la categoría más cara (según tarifa y duración) + recargo por número de tratamientos',
        'impuesto_seguro': st['tariff'].get('insuranceTax'),
        'edad': st['tariff'].get('age'),
        'paises_tratamiento': st['startConfig'].get('treatmentCountries'),
        'tratamientos': [{
            'es': t['i18n'].get('es', t['name']), 'de': t['i18n'].get('de', t['name']), 'categoria': t['cat'],
            'zona': t['region'],
            'excluye': [by_uuid[u]['i18n'].get('es') for u in t['exclusion'] if u in by_uuid],
            'preguntas_riesgo': {k: {'excluye_si_si': v.get('isStopper', False), 'texto': v.get('text', {}).get('es')}
                                 for k, v in (t.get('riskquery') or {}).items() if v.get('active')},
        } for t in sorted(ts, key=lambda t: (t['cat'], t['i18n'].get('es', '')))],
    }
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(out, len(data['tratamientos']), 'tratamientos')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'tarifas_medassure_beauty_ES.json')
