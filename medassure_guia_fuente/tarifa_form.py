"""Tariff data and document JavaScript for the fillable medassure beauty form.

The data comes from medassure_tarifas/tarifas_medassure_beauty_ES.json (extracted from the
medassurance.de calculator with medassure_tarifas/extraer_tarifas.py).
"""
import json
import os

_JSON = os.path.join(os.path.dirname(__file__), '..', 'medassure_tarifas', 'tarifas_medassure_beauty_ES.json')
DATA = json.load(open(_JSON, encoding='utf-8'))

PLAN = {'basic': 'B', 'premium': 'P'}
PRICES = {c.lower(): {PLAN[p]: [int(v) for v in vs] for p, vs in plans.items()}  # category -> tariff -> [1, 2, 5 years]
          for c, plans in DATA['precios'].items()}
SURCHARGE = [0, 0] + [int(DATA['recargo_por_n_tratamientos'][str(n)]) for n in (2, 3, 4)]  # by number of treatments

# the four liposuction variants of the web collapse into one dropdown entry; the category comes from the
# section "EN CASO DE LIPOSUCCIÓN": 1 operation a / up to 3 b, with skin tightening (laser/RF) 1 -> b, 3 -> f
LIPO_LABEL = 'Liposucción · a/b'
LIPO_CAT = {'1': {'no': 'a', 'si': 'b'}, '3': {'no': 'b', 'si': 'f'}}
SHORT = {'Lifting facial (frente, cejas, mejillas, labios, línea del mentón)':
         'Lifting facial (frente, cejas, mejillas, labios, mentón)'}

TREATMENTS = []  # (option shown in the dropdown, category; 'L' = liposuction)
ALONE = []       # cannot be combined with any other treatment (gastric balloon on the web)
CAPSULAR = []    # cannot be insured once a capsular contracture has been diagnosed
for t in DATA['tratamientos']:
    if t['es'].startswith(('Liposucción', 'Lipoaspiración')):
        if (LIPO_LABEL, 'L') not in TREATMENTS:
            TREATMENTS.append((LIPO_LABEL, 'L'))
        continue
    label = f"{SHORT.get(t['es'], t['es'])} · {t['categoria'].lower()}"
    TREATMENTS.append((label, t['categoria'].lower()))
    if len(t['excluye']) >= len(DATA['tratamientos']) - 2:
        ALONE.append(label)
    if t['preguntas_riesgo'].get('capsular', {}).get('excluye_si_si'):
        CAPSULAR.append(label)

DOC_JS = r'''
var maDoc = this;
var MA_PRICES = %(prices)s;
var MA_SUR = %(sur)s;
var MA_LIPO = %(lipo)s;
var MA_TRAT = %(trat)s;
var MA_SOLO = %(solo)s;
var MA_CAPS = %(caps)s;
function maF(n) { return maDoc.getField(n); }
function maVal(n) { var f = maF(n); return f ? String(f.valueAsString).replace(/^\s+|\s+$/g, "") : ""; }
function maOn(n) { var f = maF(n); return f ? f.value != "Off" : false; }
function maAny(names) { for (var i = 0; i < names.length; i++) if (maOn(names[i])) return true; return false; }
function maLock(n, lock) {
  var f = maF(n); if (!f) return;
  if (f.readonly != lock) f.readonly = lock;
  if (lock) { var empty = (f.type == "checkbox") ? "Off" : ""; if (String(f.value).replace(/\s+/g, "") != String(empty)) f.value = empty; }
}
function maIn(list, v) { for (var i = 0; i < list.length; i++) if (list[i] == v) return true; return false; }
function maChosen() { var r = []; for (var i = 1; i <= 4; i++) { var v = maVal("tratamiento_" + i); if (v != "") r.push(v); } return r; }
function maHasLipo() { var t = maChosen(); for (var i = 0; i < t.length; i++) if (MA_TRAT[t[i]] == "L") return true; return false; }
function maRules() {
  // Basica admits max. 3 treatments
  maLock("tratamiento_4", maOn("tarifa_basica"));
  // liposuction options only when a liposuction treatment is chosen
  var lipo = maHasLipo();
  maLock("liposuccion_1_operacion", !lipo); maLock("liposuccion_hasta_3", !lipo); maLock("tensado_cutaneo", !lipo);
}
// returns "" when the selection can be insured, otherwise the reason
function maBlock() {
  var t = maChosen(), lipo = 0;
  for (var i = 0; i < t.length; i++) {
    if (MA_TRAT[t[i]] == "L") lipo++;
    if (t.length > 1 && maIn(MA_SOLO, t[i])) return t[i].replace(/ · .*$/, "") + " no se combina con otros tratamientos";
    if (maOn("contractura_si") && maIn(MA_CAPS, t[i])) return "no asegurable con contractura capsular diagnosticada";
  }
  if (lipo > 1) return "elija Liposucción una sola vez";
  return "";
}
function maCalc() {
  maRules();
  var tar = maOn("tarifa_basica") ? "B" : (maOn("tarifa_premium") ? "P" : "");
  var d = maOn("duracion_1_ano") ? 0 : (maOn("duracion_2_anos") ? 1 : (maOn("duracion_5_anos") ? 2 : -1));
  var t = maChosen(), best = 0, unknown = false;
  if (t.length == 0) return "elija tratamiento";
  var block = maBlock();
  if (block) return block;
  for (var i = 0; i < t.length; i++) {
    var cat = MA_TRAT[t[i]];
    if (cat == "L") {
      var ops = maOn("liposuccion_hasta_3") ? "3" : (maOn("liposuccion_1_operacion") ? "1" : "");
      if (ops == "") return "marque n.º de operaciones";
      cat = MA_LIPO[ops][maOn("tensado_cutaneo") ? "si" : "no"];
    }
    if (!cat) { unknown = true; continue; }
    if (tar && d >= 0) best = Math.max(best, MA_PRICES[cat][tar][d]);
  }
  if (!tar) return "elija tarifa";
  if (d < 0) return "elija duración";
  if (unknown) return "consúltenos";
  var total = best + MA_SUR[Math.min(t.length, 4)];
  return String(total.toFixed(2)).replace(".", ",") + " €";
}
var MA_REQ = [
  ["apellidos_nombre", "Apellidos, nombre"], ["fecha_nacimiento", "Fecha de nacimiento"],
  ["calle_numero", "Calle, número"], ["cp_localidad", "Código postal y localidad"],
  ["telefono", "Teléfono"], ["email", "E-mail"], ["cirujano_clinica", "Cirujano/a y clínica"],
  ["fecha_operacion", "Fecha de la operación"], ["tratamiento_1", "Tipo de tratamiento 1"],
  ["titular_cuenta", "Titular de la cuenta"], ["direccion_titular", "Dirección del titular de la cuenta"],
  ["p2_lugar_fecha", "Lugar y fecha (página 2)"], ["p1_lugar_fecha", "Lugar y fecha (página 1)"]
];
function maEnviar() {
  if (maOn("decision_renunciar")) {
    app.alert("Ha marcado que renuncia al seguro de complicaciones.\n\nNo es necesario enviar la solicitud: basta con firmar la primera página y entregarla en la clínica.", 3);
    return;
  }
  var block = maBlock();
  if (block) {
    app.alert("Con esta selección no se puede contratar el seguro:\n\n• " + block, 1);
    return;
  }
  var miss = [];
  if (!maOn("decision_contratar")) miss.push("Su decisión (página 1)");
  for (var i = 0; i < MA_REQ.length; i++) if (maVal(MA_REQ[i][0]) == "") miss.push(MA_REQ[i][1]);
  if (!maAny(["grasa_autologa_si", "grasa_autologa_no"])) miss.push("¿Tratamiento con grasa autóloga?");
  if (!maAny(["contractura_si", "contractura_no"])) miss.push("¿Contractura capsular ya diagnosticada?");
  if (maHasLipo() && !maAny(["liposuccion_1_operacion", "liposuccion_hasta_3"])) miss.push("Liposucción: n.º de operaciones");
  if (!maAny(["tarifa_basica", "tarifa_premium"])) miss.push("Selección de tarifa");
  if (!maAny(["duracion_1_ano", "duracion_2_anos", "duracion_5_anos"])) miss.push("Duración (1, 2 o 5 años)");
  var iban = maVal("iban").replace(/[^0-9]/g, "");
  if (iban.length != 22) miss.push("IBAN (faltan dígitos: hay " + iban.length + " de 22)");
  var em = maVal("email");
  if (em != "" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) miss.push("E-mail (no parece válido)");
  if (miss.length) {
    app.alert("Antes de enviar, complete estos datos:\n\n• " + miss.join("\n• "), 1);
    return;
  }
  var msg = "Todo está completo.\n\nPrima total: " + maCalc() +
            "\n\nRecuerde firmar en las dos páginas.\n\n¿Enviar ahora la solicitud a info@medassure.es?";
  if (app.alert(msg, 2, 2) == 4) {
    maDoc.mailDoc({ bUI: true, cTo: "info@medassure.es",
      cSubject: "Solicitud medassure beauty - " + maVal("apellidos_nombre"),
      cMsg: "Adjunto la solicitud del seguro de complicaciones medassure beauty.\n\nFecha de la operación: " + maVal("fecha_operacion") });
  }
}
''' % {'prices': json.dumps(PRICES), 'sur': json.dumps(SURCHARGE), 'lipo': json.dumps(LIPO_CAT),
       'trat': json.dumps({t: cat for t, cat in TREATMENTS}, ensure_ascii=False),
       'solo': json.dumps(ALONE, ensure_ascii=False), 'caps': json.dumps(CAPSULAR, ensure_ascii=False)}
