"""Fillable versions of the medassure dental and medassure adipo forms (same features as make_form.py for beauty).

Usage: python3 make_form_dental_adipo.py dental Formulario_-_Medassure_Dental.pdf medassure_dental_Formulario_rellenable.pdf
       python3 make_form_dental_adipo.py adipo  Formulario_-_Medassure_Adipo.pdf  medassure_adipo_Formulario_rellenable.pdf

Coordinates are taken from the Chromium-generated originals (x, top in PDF points from the top-left corner).
Prices are the ones printed on each form; dental and adipo bypass/sleeve match the medassurance.de calculator
(see medassure_tarifas/tarifas_medassure_dental_adipo_ES.md).
"""
import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (NameObject, DictionaryObject, TextStringObject, ArrayObject, FloatObject,
                           NumberObject, StreamObject)

product, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
assert product in ('dental', 'adipo')
orig = PdfReader(src)
W, H = [float(v) for v in orig.pages[0].mediabox[2:]]
T = colors.Color(1, 1, 1, alpha=0)
INK = colors.Color(0.05, 0.15, 0.35)
BRAND = {'dental': colors.Color(0.1804, 0.8, 0.4431), 'adipo': colors.Color(0.6078, 0.349, 0.7137)}[product]
BAND = {'dental': colors.Color(0.09, 0.55, 0.29), 'adipo': BRAND}[product]  # darker green so white text reads

# ---- layout of each original (pdfplumber coordinates: x, top) ----
L = {
    'dental': dict(p1_decision=(544.9, 613.9), p1_sign=758.2, rows=[143.2, 170.2, 197.2, 243.0],
                   tarifa=((46.9, 363.4, 12.7), (316.1, 365.6, 12.0)), sepa=624.7, iban=632.6, p2_sign=694.5),
    'adipo': dict(p1_decision=(538.9, 607.9), p1_sign=753.0, rows=[142.5, 171.0, 199.5, 246.7],
                  tarifa=((46.9, 370.1, 12.7), (316.1, 371.6, 12.0)), sepa=629.2, iban=637.1, p2_sign=702.0),
}[product]

# ---- tariff data printed on the forms: [1, 2, 5 years], B = Básica, P = Premium ----
DENTAL_PRICES = {  # category by treatment cost
    'A': {'B': [99, 128, 215], 'P': [149, 193, 324]},
    'B': {'B': [134, 173, 290], 'P': [201, 260, 436]},
    'C': {'B': [169, 218, 365], 'P': [254, 328, 550]},
    'D': {'B': [214, 283, 490], 'P': [321, 425, 737]},
    'E': {'B': [259, 348, 615], 'P': [389, 523, 925]},
}
DENTAL_LIMITS = [[1000, 'A'], [1500, 'B'], [3000, 'C'], [5000, 'D']]  # up to (incl.) -> category, above: E
RISK_FACTOR = 1.5  # periodontitis, diabetes or smoker: +50 % (once, however many apply)
ADIPO_PRICES = {
    'A': {'B': 499, 'P': 599},  # bypass / sleeve, BMI up to 40, 29 days
    'B': {'B': 899, 'P': 999},  # bypass / sleeve, BMI over 40 up to 60
    'C': {'B': [289, 399, 499], 'P': [399, 549, 699]},  # Endomina, POSE, Overstitch
    'D': {'B': [169, 199, 249], 'P': [249, 279, 299]},  # gastric balloon
}
ADIPO_TYPES = {'bypass': 'bar', 'manga': 'bar', 'balon': 'D', 'endomina': 'C', 'pose': 'C', 'overstitch': 'C'}

ov = 'overlay.pdf'
c = canvas.Canvas(ov, pagesize=(W, H))
af = c.acroForm


def text(name, tip, x, top, w, h, size=9.5, **kw):
    af.textfield(name=name, tooltip=tip, x=x, y=H - top - h, width=w, height=h, fontName='Helvetica', fontSize=size,
                 borderWidth=0, borderColor=T, fillColor=T, textColor=kw.pop('textColor', INK), forceBorder=False, **kw)


GROUPS = {}


def radio(name, value, tip, x, top, s):
    # independent tick box (toggles on/off in every viewer); siblings un-tick each other via JS in Acrobat
    fname = f'{name}_{value}'
    GROUPS.setdefault(name, []).append(fname)
    check(fname, tip, x, top, s)


def check(name, tip, x, top, s):
    af.checkbox(name=name, tooltip=tip, x=x, y=H - top - s, size=s, buttonStyle='cross', shape='square',
                borderWidth=0, borderColor=T, fillColor=T, textColor=INK, forceBorder=False, checked=False)


def line_field(name, tip, x, ul, w=246.7, h=10.5, size=9.5):
    text(name, tip, x + 1, ul - h - 0.5, w - 2, h, size=size)


def white(x, top, w, h):
    c.setFillColor(colors.white); c.rect(x, H - top - h, w, h, stroke=0, fill=1)


# ---------- page 1 ----------
y1, y2 = L['p1_decision']
radio('decision', 'contratar', 'Deseo contratar el seguro', 50.6, y1, 13.5)
radio('decision', 'renunciar', 'Renuncio al seguro', 50.6, y2, 13.5)
text('p1_lugar_fecha', 'Lugar y fecha', 37, L['p1_sign'] - 21.5, 242, 21, size=11)
text('p1_firma', 'Firma del/de la paciente', 316, L['p1_sign'] - 21.5, 242, 21, size=11)
c.showPage()

# ---------- page 2 ----------
af = c.acroForm
r = L['rows']
line_field('apellidos_nombre', 'Apellidos, nombre', 36.7, r[0]); line_field('fecha_nacimiento', 'Fecha de nacimiento (DD/MM/AAAA)', 312, r[0])
line_field('calle_numero', 'Calle, número', 36.7, r[1]); line_field('cp_localidad', 'Código postal y localidad', 312, r[1])
line_field('telefono', 'Teléfono', 36.7, r[2]); line_field('email', 'E-mail', 312, r[2])

if product == 'dental':
    line_field('odontologo_clinica', 'Odontólogo/a y clínica', 36.7, r[3])
    line_field('fecha_inicio', 'Fecha de inicio del tratamiento (DD/MM/AAAA)', 312, r[3])
    for name, tip, x, top in [('tipo_implantes', 'Implantes', 47.6, 266.6), ('tipo_puentes', 'Puentes', 108.4, 266.6),
                              ('tipo_coronas', 'Coronas', 47.6, 283.1), ('tipo_supraestructuras', 'Supraestructuras', 106.1, 283.1),
                              ('tipo_otros', 'Otros', 47.6, 296.6)]:
        check(name, 'Tipo de tratamiento: ' + tip, x, top, 11.2)
    text('tipo_otros_detalle', 'Otros: indique qué tratamiento', 92, 297, 125, 10.5, size=8.5)
    text('coste_total', 'Coste total del tratamiento según presupuesto (en euros)', 227.5, 277, 121, 10.5)
    # remove "N.º DE PIEZAS / IMPLANTES" (label and its line)
    white(224, 295.5, 138, 35)
    for key, top in [('periodontitis', 266.6), ('diabetes', 281.6), ('fumador', 296.6)]:
        radio(key, 'si', f'{key.capitalize()}: Sí', 437.6, top, 11.2)
        radio(key, 'no', f'{key.capitalize()}: No', 469.9, top, 11.2)
    for x, v in [(378.4, '1_ano'), (439.1, '2_anos'), (502.9, '5_anos')]:
        radio('duracion', v, 'Duración: ' + v.replace('_', ' ').replace('ano', 'año'), x, 427.9, 11.2)
else:
    line_field('cirujano_clinica', 'Cirujano/a y clínica', 36.7, r[3])
    line_field('fecha_intervencion', 'Fecha de la intervención (DD/MM/AAAA)', 312, r[3])
    for v, tip, x, top in [('bypass', 'Bypass gástrico', 47.6, 273.4), ('manga', 'Manga gástrica', 131.6, 273.4),
                           ('balon', 'Balón gástrico', 215.6, 273.4), ('endomina', 'Endomina', 47.6, 290.6),
                           ('pose', 'POSE', 112.1, 290.6), ('overstitch', 'Overstitch', 160.1, 290.6)]:
        radio('intervencion', v, 'Tipo de intervención: ' + tip, x, top, 11.2)
    text('peso', 'Peso en kg', 337.7, 280.7, 188, 10.5)
    text('altura', 'Altura en cm', 337.7, 321.2, 186, 10.5)
    text('imc', 'IMC (se calcula automáticamente en Adobe Acrobat Reader)', 400, 259.5, 150, 9, size=8,
         textColor=colors.Color(0.35, 0.35, 0.35))
    radio('duracion', '29_dias', 'Bypass / manga gástrica: 29 días de cobertura', 393.4, 426.4, 11.2)
    for x, v in [(378.4, '1_ano'), (439.1, '2_anos'), (502.9, '5_anos')]:
        radio('duracion', v, 'Procedimiento endoscópico: ' + v.replace('_', ' ').replace('ano', 'año'), x, 505.9, 11.2)

(bx, btop, bs), (px, ptop, ps) = L['tarifa']
radio('tarifa', 'basica', 'Tarifa Básica', bx, btop, bs)
radio('tarifa', 'premium', 'Tarifa Premium', px, ptop, ps)

# SEPA
line_field('titular_cuenta', 'Titular de la cuenta', 36.7, L['sepa'])
line_field('direccion_titular', 'Calle, número / CP y localidad del titular', 312, L['sepa'])
# IBAN: one continuous comb field (22 digits after "ES") over a redrawn uniform grid
gx0, gx1, gtop, gh, n = 94.9, 523.9, L['iban'], 21.7, 22
cw = (gx1 - gx0) / n
white(gx0 - 2, gtop - 2, gx1 - gx0 + 4, gh + 4)
c.setStrokeColor(colors.Color(0.6, 0.63, 0.65)); c.setLineWidth(0.75)
c.rect(gx0, H - gtop - gh, gx1 - gx0, gh, stroke=1, fill=0)
for i in range(1, n):
    x = gx0 + i * cw
    if i in (2, 6, 10, 14, 18):
        c.setStrokeColor(colors.Color(0.25, 0.25, 0.25)); c.setLineWidth(1.6)
    else:
        c.setStrokeColor(colors.Color(0.6, 0.63, 0.65)); c.setLineWidth(0.6)
    c.line(x, H - gtop - gh, x, H - gtop)
text('iban', 'IBAN: escriba los 22 dígitos seguidos (sin ES ni espacios)', gx0, gtop, gx1 - gx0, gh, size=12, maxlen=n,
     fieldFlags='comb')

# automatic premium in the free space between IBAN and signatures
btop2 = L['iban'] + 28.5
c.setFillColor(BAND); c.roundRect(312, H - btop2 - 22, 246.7, 22, 4, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 9.5); c.drawString(322, H - btop2 - 14.5, 'PRIMA ÚNICA TOTAL')
text('prima_total', 'Prima total (se calcula automáticamente en Adobe Acrobat Reader)', 420, btop2 + 2.5, 134, 17,
     size=12.5, textColor=colors.white)

text('p2_lugar_fecha', 'Lugar, fecha', 37, L['p2_sign'] - 14, 244, 13.5, size=10)
text('p2_firma', 'Firma del tomador y titular de la cuenta', 313, L['p2_sign'] - 14, 244, 13.5, size=10)
c.showPage(); c.save()

w = PdfWriter(clone_from=ov)
for i, page in enumerate(w.pages):
    page.merge_page(orig.pages[i], over=False)  # original underneath: white patches and redrawn grid stay on top
w.set_need_appearances_writer(True)


def js_action(code):
    return DictionaryObject({NameObject('/S'): NameObject('/JavaScript'), NameObject('/JS'): TextStringObject(code)})


def widgets():
    for page in w.pages:
        for ref in page.get('/Annots', []):
            a = ref.get_object()
            fld = a if '/T' in a else a.get('/Parent', a).get_object()
            yield page, ref, a, fld


sib = {f: [g for g in fs if g != f] for fs in GROUPS.values() for f in fs}
for page, ref, a, fld in widgets():
    name = str(fld.get('/T'))
    if fld.get('/FT') == '/Btn' and '/AP' in a:
        x0, y0, x1, y1 = [float(v) for v in a['/Rect']]
        sz = min(x1 - x0, y1 - y0); m = sz * 0.24; lw = max(1.3, sz * 0.13)
        path = (f"q .05 .15 .35 RG {lw:.2f} w 1 J {m:.2f} {m:.2f} m {sz-m:.2f} {sz-m:.2f} l "
                f"{m:.2f} {sz-m:.2f} m {sz-m:.2f} {m:.2f} l S Q").encode()
        for st, ref2 in a['/AP']['/N'].items():
            if st != '/Off': ref2.get_object().set_data(path)
        if '/D' in a['/AP']: del a['/AP']['/D']
        if name in sib:
            a[NameObject('/A')] = js_action('if (event.target.value != "Off") {' + ''.join(
                f' this.getField("{o}").value = "Off";' for o in sib[name]) + ' }')
    if name == 'iban':
        a[NameObject('/AA')] = DictionaryObject({NameObject('/K'): js_action(
            'if (!event.willCommit) event.change = event.change.replace(/[^0-9]/g, "");')})
    if name in ('coste_total', 'peso', 'altura'):
        a[NameObject('/AA')] = DictionaryObject({NameObject('/K'): js_action(
            'if (!event.willCommit) event.change = event.change.replace(/[^0-9.,]/g, "");')})
    if name in ('prima_total', 'imc'):
        a[NameObject('/Q')] = NumberObject(2)
        a[NameObject('/Ff')] = NumberObject(1)
        a[NameObject('/AA')] = DictionaryObject({NameObject('/C'): js_action(
            'event.value = maCalc();' if name == 'prima_total' else 'event.value = maImcText();')})
co = [ref for _, ref, _, fld in widgets() if str(fld.get('/T')) in ('imc', 'prima_total')]
w._root_object['/AcroForm'][NameObject('/CO')] = ArrayObject(co)

# ---- document-level JavaScript (Acrobat / Acrobat Reader) ----
COMMON_JS = r'''
var maDoc = this;
function maF(n) { return maDoc.getField(n); }
function maVal(n) { var f = maF(n); return f ? String(f.valueAsString).replace(/^\s+|\s+$/g, "") : ""; }
function maOn(n) { var f = maF(n); return f ? f.value != "Off" : false; }
function maAny(names) { for (var i = 0; i < names.length; i++) if (maOn(names[i])) return true; return false; }
function maLock(n, lock) {
  var f = maF(n); if (!f) return;
  if (f.readonly != lock) f.readonly = lock;
  if (lock) { var empty = (f.type == "checkbox") ? "Off" : ""; if (String(f.value).replace(/\s+/g, "") != String(empty)) f.value = empty; }
}
// "3.500", "3500,50", "3.500,50 €" -> number (NaN when empty or not a number)
function maNum(s) {
  s = String(s).replace(/[^0-9.,]/g, "");
  if (s == "") return NaN;
  if (s.indexOf(",") >= 0) s = s.replace(/\./g, "").replace(",", ".");
  else if (/^\d{1,3}(\.\d{3})+$/.test(s)) s = s.replace(/\./g, "");
  return parseFloat(s);
}
function maEuro(v) {
  var s = v.toFixed(2).split("."), i = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return i + "," + s[1] + " €";
}
function maTar() { return maOn("tarifa_basica") ? "B" : (maOn("tarifa_premium") ? "P" : ""); }
function maDur() { return maOn("duracion_1_ano") ? 0 : (maOn("duracion_2_anos") ? 1 : (maOn("duracion_5_anos") ? 2 : -1)); }
function maEnviar() {
  if (maOn("decision_renunciar")) {
    app.alert("Ha marcado que renuncia al seguro de complicaciones.\n\nNo es necesario enviar la solicitud: basta con firmar la primera página y entregarla en la clínica.", 3);
    return;
  }
  var block = maBlock();
  if (block) {
    app.alert("Con estos datos no se puede contratar el seguro:\n\n• " + block, 1);
    return;
  }
  var miss = [];
  if (!maOn("decision_contratar")) miss.push("Su decisión (página 1)");
  for (var i = 0; i < MA_REQ.length; i++) if (maVal(MA_REQ[i][0]) == "") miss.push(MA_REQ[i][1]);
  maMissing(miss);
  if (!maAny(["tarifa_basica", "tarifa_premium"])) miss.push("Selección de tarifa");
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
      cSubject: "Solicitud medassure %(product)s - " + maVal("apellidos_nombre"),
      cMsg: "Adjunto la solicitud del seguro de complicaciones medassure %(product)s.\n\n" + MA_FECHA[1] + ": " + maVal(MA_FECHA[0]) });
  }
}
''' % {'product': product}

DENTAL_JS = r'''
var MA_PRICES = %(prices)s;
var MA_LIMITS = %(limits)s;
var MA_RISK = %(risk)s;
var MA_TIPOS = ["tipo_implantes", "tipo_puentes", "tipo_coronas", "tipo_supraestructuras", "tipo_otros"];
var MA_FACT = [["periodontitis", "Periodontitis"], ["diabetes", "Diabetes"], ["fumador", "Fumador/a"]];
var MA_FECHA = ["fecha_inicio", "Fecha de inicio del tratamiento"];
var MA_REQ = [
  ["apellidos_nombre", "Apellidos, nombre"], ["fecha_nacimiento", "Fecha de nacimiento"],
  ["calle_numero", "Calle, número"], ["cp_localidad", "Código postal y localidad"],
  ["telefono", "Teléfono"], ["email", "E-mail"], ["odontologo_clinica", "Odontólogo/a y clínica"],
  ["fecha_inicio", "Fecha de inicio del tratamiento"], ["coste_total", "Coste total (presupuesto)"],
  ["titular_cuenta", "Titular de la cuenta"], ["direccion_titular", "Dirección del titular de la cuenta"],
  ["p2_lugar_fecha", "Lugar y fecha (página 2)"], ["p1_lugar_fecha", "Lugar y fecha (página 1)"]
];
function maImcText() { return ""; }
function maCat() {
  var v = maNum(maVal("coste_total"));
  if (isNaN(v) || v <= 0) return "";
  for (var i = 0; i < MA_LIMITS.length; i++) if (v <= MA_LIMITS[i][0]) return MA_LIMITS[i][1];
  return "E";
}
function maBlock() { return ""; }
function maCalc() {
  maLock("tipo_otros_detalle", !maOn("tipo_otros"));
  var cat = maCat(), tar = maTar(), d = maDur(), risk = false;
  if (maVal("coste_total") == "") return "indique el coste";
  if (!cat) return "coste no válido";
  for (var i = 0; i < MA_FACT.length; i++) {
    var k = MA_FACT[i][0];
    if (!maAny([k + "_si", k + "_no"])) return "conteste factores de riesgo";
    if (maOn(k + "_si")) risk = true;
  }
  if (!tar) return "elija tarifa";
  if (d < 0) return "elija duración";
  var total = MA_PRICES[cat][tar][d] * (risk ? MA_RISK : 1);
  return maEuro(total);
}
function maMissing(miss) {
  if (!maAny(MA_TIPOS)) miss.push("Tipo de tratamiento");
  if (maOn("tipo_otros") && maVal("tipo_otros_detalle") == "") miss.push("Tipo de tratamiento: indique cuál es «Otros»");
  if (maVal("coste_total") != "" && !maCat()) miss.push("Coste total (no es un importe válido)");
  for (var i = 0; i < MA_FACT.length; i++)
    if (!maAny([MA_FACT[i][0] + "_si", MA_FACT[i][0] + "_no"])) miss.push("Factor de riesgo: " + MA_FACT[i][1]);
  if (!maAny(["duracion_1_ano", "duracion_2_anos", "duracion_5_anos"])) miss.push("Duración (1, 2 o 5 años)");
}
''' % {'prices': json.dumps(DENTAL_PRICES), 'limits': json.dumps(DENTAL_LIMITS), 'risk': RISK_FACTOR}

ADIPO_JS = r'''
var MA_PRICES = %(prices)s;
var MA_TYPES = %(types)s;
var MA_FECHA = ["fecha_intervencion", "Fecha de la intervención"];
var MA_REQ = [
  ["apellidos_nombre", "Apellidos, nombre"], ["fecha_nacimiento", "Fecha de nacimiento"],
  ["calle_numero", "Calle, número"], ["cp_localidad", "Código postal y localidad"],
  ["telefono", "Teléfono"], ["email", "E-mail"], ["cirujano_clinica", "Cirujano/a y clínica"],
  ["fecha_intervencion", "Fecha de la intervención"], ["peso", "Peso"], ["altura", "Altura"],
  ["titular_cuenta", "Titular de la cuenta"], ["direccion_titular", "Dirección del titular de la cuenta"],
  ["p2_lugar_fecha", "Lugar y fecha (página 2)"], ["p1_lugar_fecha", "Lugar y fecha (página 1)"]
];
function maType() { for (var k in MA_TYPES) if (maOn("intervencion_" + k)) return MA_TYPES[k]; return ""; }
function maImc() {
  var kg = maNum(maVal("peso")), cm = maNum(maVal("altura"));
  if (isNaN(kg) || isNaN(cm) || kg <= 0 || cm <= 0) return NaN;
  if (cm < 3) cm = cm * 100;  // height typed in metres
  return kg / ((cm / 100) * (cm / 100));
}
function maImcText() { var b = maImc(); return isNaN(b) ? "" : "IMC: " + b.toFixed(1).replace(".", ","); }
function maRules() {
  // bypass / sleeve: 29 days only; endoscopic: 1, 2 or 5 years
  var t = maType(), bar = (t == "bar"), endo = (t == "C" || t == "D");
  if (bar && !maOn("duracion_29_dias")) maF("duracion_29_dias").value = "Yes";
  maLock("duracion_29_dias", endo);
  maLock("duracion_1_ano", bar); maLock("duracion_2_anos", bar); maLock("duracion_5_anos", bar);
}
function maBlock() {
  var b = maImc();
  if (!isNaN(b) && b > 60) return "IMC superior a 60 (" + b.toFixed(1).replace(".", ",") + "): no es asegurable";
  return "";
}
function maCalc() {
  maRules();
  var t = maType(), tar = maTar(), b = maImc();
  if (!t) return "elija intervención";
  if (isNaN(b)) return "indique peso y altura";
  var block = maBlock();
  if (block) return "IMC > 60: no asegurable";
  if (!tar) return "elija tarifa";
  if (t == "bar") return maEuro(MA_PRICES[b > 40 ? "B" : "A"][tar]);
  var d = maDur();
  if (d < 0) return "elija duración";
  return maEuro(MA_PRICES[t][tar][d]);
}
function maMissing(miss) {
  var t = maType();
  if (!t) miss.push("Tipo de intervención");
  if (maVal("peso") != "" && maVal("altura") != "" && isNaN(maImc())) miss.push("Peso y altura (no son números válidos)");
  if ((t == "C" || t == "D") && maDur() < 0) miss.push("Duración (1, 2 o 5 años)");
}
''' % {'prices': json.dumps(ADIPO_PRICES), 'types': json.dumps(ADIPO_TYPES)}

w.add_js(COMMON_JS + (DENTAL_JS if product == 'dental' else ADIPO_JS))


# ---- on-screen buttons in the footer (not printed) ----
def button(page, rect, name, label, tip, rgb, action):
    x0, y0, x1, y1 = rect; bw, bh = x1 - x0, y1 - y0
    fs = 8.5; tw = stringWidth(label, 'Helvetica-Bold', fs)
    ap = StreamObject()
    ap.set_data((f"q {rgb[0]} {rgb[1]} {rgb[2]} rg 0 0 {bw:.2f} {bh:.2f} re f Q "
                 f"BT /HeBo {fs} Tf 1 1 1 rg {(bw - tw) / 2:.2f} {(bh - 6) / 2:.2f} Td ({label}) Tj ET").encode('latin-1'))
    ap.update({NameObject('/Type'): NameObject('/XObject'), NameObject('/Subtype'): NameObject('/Form'),
               NameObject('/BBox'): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(bw), FloatObject(bh)]),
               NameObject('/Resources'): DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/HeBo'): DictionaryObject({
                   NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'),
                   NameObject('/BaseFont'): NameObject('/Helvetica-Bold'), NameObject('/Encoding'): NameObject('/WinAnsiEncoding')})})})})
    btn = DictionaryObject({
        NameObject('/Type'): NameObject('/Annot'), NameObject('/Subtype'): NameObject('/Widget'),
        NameObject('/FT'): NameObject('/Btn'), NameObject('/Ff'): NumberObject(1 << 16),
        NameObject('/T'): TextStringObject(name), NameObject('/TU'): TextStringObject(tip),
        NameObject('/Rect'): ArrayObject([FloatObject(v) for v in rect]), NameObject('/F'): NumberObject(0),
        NameObject('/MK'): DictionaryObject({NameObject('/BG'): ArrayObject([FloatObject(v) for v in rgb]),
                                             NameObject('/CA'): TextStringObject(label)}),
        NameObject('/DA'): TextStringObject(f'/Helv {fs} Tf 1 1 1 rg'),
        NameObject('/AP'): DictionaryObject({NameObject('/N'): w._add_object(ap)}),
        NameObject('/A'): action, NameObject('/P'): page.indirect_reference})
    ref = w._add_object(btn)
    page[NameObject('/Annots')].append(ref)
    w._root_object['/AcroForm']['/Fields'].append(ref)


GREEN, BLUEB, RED = (0.13, 0.55, 0.33), (0.16, 0.45, 0.75), (0.80, 0.22, 0.18)
for idx, page in enumerate(w.pages, start=1):
    yb, yt = H - 831.0, H - 815.0
    button(page, (340.0, yb, 436.0, yt), f'enviar_{idx}', 'Comprobar y enviar',
           'Comprueba que no falte nada y envía la solicitud por correo', GREEN, js_action('maEnviar();'))
    button(page, (442.0, yb, 500.0, yt), f'imprimir_{idx}', 'Imprimir', 'Imprimir el formulario', BLUEB,
           js_action('this.print({bUI: true, bShrinkToFit: true});'))
    button(page, (506.0, yb, 558.7, yt), f'borrar_todo_{idx}', 'Borrar todo', 'Borrar todos los datos del formulario', RED,
           DictionaryObject({NameObject('/S'): NameObject('/ResetForm')}))

# ---- tab order: top-to-bottom, left-to-right; buttons last ----
for page in w.pages:
    annots = [r for r in page['/Annots']]
    def key(r):
        a = r.get_object(); x0, y0, x1, y1 = [float(v) for v in a['/Rect']]
        is_btn = int(a.get('/Ff', 0)) & (1 << 16)
        return (1 if is_btn else 0, round(-y1 / 6), x0)
    page[NameObject('/Annots')] = ArrayObject(sorted(annots, key=key))
    page[NameObject('/Tabs')] = NameObject('/R')

title = {'dental': 'medassure dental – Información económica y solicitud',
         'adipo': 'medassure adipo – Información económica y solicitud'}[product]
w.add_metadata({'/Title': title, '/Author': 'IberAssekuranz Brokers'})
with open(out, 'wb') as f:
    w.write(f)
r = PdfReader(out); print(out, 'fields:', len(r.get_fields()))
