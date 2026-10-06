import sys, json
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (NameObject, DictionaryObject, TextStringObject, ArrayObject, FloatObject,
                           NumberObject, StreamObject)

src, out = sys.argv[1], sys.argv[2]
orig = PdfReader(src)
W1, H1 = [float(v) for v in orig.pages[0].mediabox[2:]]
W2, H2 = [float(v) for v in orig.pages[1].mediabox[2:]]
T = colors.Color(1, 1, 1, alpha=0)
INK = colors.Color(0.05, 0.15, 0.35)
BLUE = colors.Color(0.16862746, 0.56078436, 0.84705886)

# ---- tariff data (same as the printed table / customer letter) ----
PRICES = {  # category -> tariff -> [1, 2, 5 years]
    'a': {'B': [69, 99, 129], 'P': [99, 129, 149]},
    'b': {'B': [99, 129, 159], 'P': [149, 179, 199]},
    'c': {'B': [169, 219, 269], 'P': [249, 299, 329]},
    'd': {'B': [189, 239, 289], 'P': [279, 349, 399]},
    'e': {'B': [289, 429, 599], 'P': [429, 599, 799]},
}
SURCHARGE = [0, 0, 50, 75, 100]          # by number of treatments
TENSADO = {'a': 30, 'b': 60}             # skin tightening with liposuction
TREATMENTS = [  # (option shown in the dropdown, category; 'L' = liposuction, category from section "EN CASO DE LIPOSUCCIÓN")
    ('Párpados (blefaroplastia) · a', 'a'),
    ('Cabello (injerto capilar) · a', 'a'),
    ('Liposucción · a/b', 'L'),
    ('Lifting facial / cervical · b', 'b'),
    ('Labioplastia · b', 'b'),
    ('Lifting de brazos · c', 'c'),
    ('Lifting de abdomen (abdominoplastia) · c', 'c'),
    ('Lifting de muslos · c', 'c'),
    ('Nariz (rinoplastia) · c', 'c'),
    ('Balón gástrico · c', 'c'),
    ('Otro tratamiento de categoría c', 'c'),
    ('Body lift · d', 'd'),
    ('Mastopexia · d', 'd'),
    ('Mastectomía · d', 'd'),
    ('Reducción mamaria · d', 'd'),
    ('Retirada de implantes · d', 'd'),
    ('Aumento mamario con implante · e', 'e'),
    ('Cambio de implante · e', 'e'),
    ('Reducción gástrica · e', 'e'),
]

ov = 'overlay.pdf'
c = canvas.Canvas(ov, pagesize=(W1, H1))
af = c.acroForm


def text(name, tip, x, top, w, h, H, size=9.5, **kw):
    af.textfield(name=name, tooltip=tip, x=x, y=H - top - h, width=w, height=h, fontName='Helvetica', fontSize=size,
                 borderWidth=0, borderColor=T, fillColor=T, textColor=kw.pop('textColor', INK), forceBorder=False, **kw)


def combo(name, tip, x, top, w, h, H, options, size=9.5):
    af.choice(name=name, tooltip=tip, value=' ', options=[' '] + options, x=x, y=H - top - h, width=w, height=h,
              fieldFlags='combo edit', fontName='Helvetica', fontSize=size,
              borderWidth=0, borderColor=T, fillColor=T, textColor=INK, forceBorder=False)


GROUPS = {}


def radio(name, value, tip, x, top, s, H):
    # independent tick box (toggles on/off in every viewer); siblings un-tick each other via JS in Acrobat
    fname = f'{name}_{value}'
    GROUPS.setdefault(name, []).append(fname)
    af.checkbox(name=fname, tooltip=tip, x=x, y=H - top - s, size=s, buttonStyle='cross', shape='square',
                borderWidth=0, borderColor=T, fillColor=T, textColor=INK, forceBorder=False, checked=False)


def check(name, tip, x, top, s, H):
    af.checkbox(name=name, tooltip=tip, x=x, y=H - top - s, size=s, buttonStyle='cross', shape='square',
                borderWidth=0, borderColor=T, fillColor=T, textColor=INK, forceBorder=False, checked=False)


# ---------- page 1 ----------
H = H1
radio('decision', 'contratar', 'Deseo contratar el seguro', 44.5, 524, 14, H)
radio('decision', 'renunciar', 'Renuncio al seguro', 44.5, 600, 14, H)
text('p1_lugar_fecha', 'Lugar y fecha', 36, 728, 243, 21, H, size=11)
text('p1_firma', 'Firma del/de la paciente', 315, 728, 244, 21, H, size=11)
c.showPage()

# ---------- page 2 ----------
c.setPageSize((W2, H2)); H = H2; af = c.acroForm
rows = [(154, 'apellidos_nombre', 'Apellidos, nombre', 'fecha_nacimiento', 'Fecha de nacimiento (DD.MM.AAAA)'),
        (173, 'calle_numero', 'Calle, número', 'cp_localidad', 'Código postal y localidad'),
        (191, 'telefono', 'Teléfono', 'email', 'E-mail'),
        (230, 'cirujano_clinica', 'Cirujano/a y clínica', 'fecha_operacion', 'Fecha de la operación (DD.MM.AAAA)')]
for top, n1, t1, n2, t2 in rows:
    text(n1, t1, 35, top - 11, 248, 10.5, H)
    text(n2, t2, 312, top - 11, 248, 10.5, H)
opts = [t for t, _ in TREATMENTS]
for i, (x, top) in enumerate([(35, 249), (312, 249), (35, 268), (312, 268)], start=1):
    combo(f'tratamiento_{i}', f'Tipo de tratamiento {i}: elija de la lista o escríbalo', x, top - 11, 248, 10.5, H, opts)
radio('liposuccion', '1_operacion', '1 operación (a)', 43.3, 289.5, 12.4, H)
radio('liposuccion', 'hasta_3', 'Hasta 3 operaciones (b)', 129.3, 289.5, 12.4, H)
check('tensado_cutaneo', 'Con tensado cutáneo', 43.3, 305.2, 11.8, H)
radio('grasa_autologa', 'si', 'Tratamiento con grasa autóloga: Sí', 305.8, 289.5, 12.4, H)
radio('grasa_autologa', 'no', 'Tratamiento con grasa autóloga: No', 343.5, 289.5, 12.4, H)
radio('contractura', 'si', 'Contractura capsular diagnosticada: Sí', 305.8, 317.6, 12.4, H)
radio('contractura', 'no', 'Contractura capsular diagnosticada: No', 343.5, 317.6, 12.4, H)
radio('tarifa', 'basica', 'Tarifa Básica', 146.2, 442.9, 14.1, H)
radio('tarifa', 'premium', 'Tarifa Premium', 210.2, 442.9, 14.1, H)
for x, v in [(372.1, '1_ano'), (437.3, '2_anos'), (504.8, '5_anos')]:
    radio('duracion', v, 'Duración: ' + v.replace('_', ' ').replace('ano', 'año'), x, 472.7, 11.8, H)

# tariff band: replace the right-hand note with the automatic total
c.setFillColor(BLUE); c.rect(300, H - 461.5, 255, 23, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 9.5); c.drawString(316, H - 453.6, 'PRIMA TOTAL')
text('prima_total', 'Prima total (se calcula automáticamente en Adobe Acrobat Reader)', 385, 441.5, 165, 17, H,
     size=13, textColor=colors.white)
# ...and move that note into the table header
c.setFillColor(colors.Color(0.35, 0.35, 0.35)); c.setFont('Helvetica-Bold', 6.3)
c.drawString(162, H - 482.2, '·  PRECIO BÁSICA / PREMIUM')

text('titular_cuenta', 'Titular de la cuenta', 35, 655, 248, 10.5, H)
text('direccion_titular', 'Calle, número / CP y localidad del titular', 312, 655, 248, 10.5, H)
# IBAN: one continuous comb field (22 digits after "ES") over a redrawn uniform grid
gx0, gx1, gtop, gh, n = 91.6, 501.4, 673.4, 16.9, 22
cw = (gx1 - gx0) / n
c.setFillColor(colors.white); c.setStrokeColor(colors.white)
c.rect(gx0 - 2, H - gtop - gh - 2, gx1 - gx0 + 4, gh + 4, stroke=0, fill=1)
c.setStrokeColor(colors.Color(0.6, 0.6, 0.6)); c.setLineWidth(0.6)
c.rect(gx0, H - gtop - gh, gx1 - gx0, gh, stroke=1, fill=0)
for i in range(1, n):
    x = gx0 + i * cw
    if i in (2, 6, 10, 14, 18):
        c.setStrokeColor(colors.Color(0.25, 0.25, 0.25)); c.setLineWidth(1.6)
    else:
        c.setStrokeColor(colors.Color(0.6, 0.6, 0.6)); c.setLineWidth(0.6)
    c.line(x, H - gtop - gh, x, H - gtop)
text('iban', 'IBAN: escriba los 22 dígitos seguidos (sin ES ni espacios)', gx0, gtop, gx1 - gx0, gh, H, size=11, maxlen=n, fieldFlags='comb')
text('p2_lugar_fecha', 'Lugar, fecha', 36, 693, 244, 13.5, H, size=10)
text('p2_firma', 'Firma del tomador y titular de la cuenta', 315, 693, 244, 13.5, H, size=10)
# fix section number 5 -> 4 (sections go 1,2,3,5)
cx, cy, r = 33.7 + 14.1 / 2, H - (632.9 + 13.5 / 2), 7.2
c.setFillColor(BLUE); c.circle(cx, cy, r, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 7.5); c.drawCentredString(cx, cy - 2.6, '4')
c.showPage(); c.save()

w = PdfWriter(clone_from=ov)
for i, page in enumerate(w.pages):
    page.merge_page(orig.pages[i], over=False)
w.set_need_appearances_writer(True)


def js_action(code):
    return DictionaryObject({NameObject('/S'): NameObject('/JavaScript'), NameObject('/JS'): TextStringObject(code)})


def widgets():
    for page in w.pages:
        for ref in page.get('/Annots', []):
            a = ref.get_object()
            fld = a if '/T' in a else a.get('/Parent', a).get_object()
            yield page, ref, a, fld


# our own centred X for every tick box + exclusive groups (Acrobat)
sib = {f: [g for g in fs if g != f] for fs in GROUPS.values() for f in fs}
for page, ref, a, fld in widgets():
    name = str(fld.get('/T'))
    if fld.get('/FT') == '/Btn' and '/AP' in a:
        x0, y0, x1, y1 = [float(v) for v in a['/Rect']]
        sz = min(x1 - x0, y1 - y0); m = sz * 0.24; lw = max(1.3, sz * 0.13)
        path = (f"q .05 .15 .35 RG {lw:.2f} w 1 J {m:.2f} {m:.2f} m {sz-m:.2f} {sz-m:.2f} l S "
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
    if name == 'prima_total':
        a[NameObject('/Q')] = NumberObject(2)
        a[NameObject('/Ff')] = NumberObject(1)
        a[NameObject('/AA')] = DictionaryObject({NameObject('/C'): js_action('event.value = maCalc();')})
        w._root_object['/AcroForm'][NameObject('/CO')] = ArrayObject([ref])

# ---- document-level JavaScript (Acrobat / Acrobat Reader) ----
DOC_JS = r'''
var maDoc = this;
var MA_PRICES = %(prices)s;
var MA_SUR = %(sur)s;
var MA_TENS = %(tens)s;
var MA_TRAT = %(trat)s;
function maF(n) { return maDoc.getField(n); }
function maVal(n) { var f = maF(n); return f ? String(f.valueAsString).replace(/^\s+|\s+$/g, "") : ""; }
function maOn(n) { var f = maF(n); return f ? f.value != "Off" : false; }
function maAny(names) { for (var i = 0; i < names.length; i++) if (maOn(names[i])) return true; return false; }
function maLock(n, lock) {
  var f = maF(n); if (!f) return;
  if (f.readonly != lock) f.readonly = lock;
  if (lock) { var empty = (f.type == "checkbox") ? "Off" : ""; if (String(f.value).replace(/\s+/g, "") != String(empty)) f.value = empty; }
}
function maHasLipo() { for (var i = 1; i <= 4; i++) if (MA_TRAT[maVal("tratamiento_" + i)] == "L") return true; return false; }
function maRules() {
  // Basica admits max. 3 treatments
  maLock("tratamiento_4", maOn("tarifa_basica"));
  // liposuction options only when a liposuction treatment is chosen
  var lipo = maHasLipo();
  maLock("liposuccion_1_operacion", !lipo); maLock("liposuccion_hasta_3", !lipo); maLock("tensado_cutaneo", !lipo);
}
function maCalc() {
  maRules();
  var tar = maOn("tarifa_basica") ? "B" : (maOn("tarifa_premium") ? "P" : "");
  var d = maOn("duracion_1_ano") ? 0 : (maOn("duracion_2_anos") ? 1 : (maOn("duracion_5_anos") ? 2 : -1));
  var n = 0, best = 0, unknown = false, lipoCat = "";
  for (var i = 1; i <= 4; i++) {
    var v = maVal("tratamiento_" + i);
    if (v == "") continue;
    n++;
    var cat = MA_TRAT[v];
    if (cat == "L") {
      cat = maOn("liposuccion_hasta_3") ? "b" : (maOn("liposuccion_1_operacion") ? "a" : "");
      if (cat == "") return "marque n.º de operaciones";
      lipoCat = cat;
    }
    if (!cat) { unknown = true; continue; }
    if (tar && d >= 0) best = Math.max(best, MA_PRICES[cat][tar][d]);
  }
  if (n == 0) return "elija tratamiento";
  if (!tar) return "elija tarifa";
  if (d < 0) return "elija duración";
  if (unknown) return "consúltenos";
  var total = best + MA_SUR[Math.min(n, 4)];
  if (lipoCat && maOn("tensado_cutaneo")) total += MA_TENS[lipoCat];
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
''' % {'prices': json.dumps(PRICES), 'sur': json.dumps(SURCHARGE), 'tens': json.dumps(TENSADO),
       'trat': json.dumps({t: cat for t, cat in TREATMENTS}, ensure_ascii=False)}
w.add_js(DOC_JS)


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
for idx, (page, Hp, top) in enumerate([(w.pages[0], H1, 808.0), (w.pages[1], H2, 818.0)], start=1):
    yb, yt = Hp - top - 16, Hp - top
    button(page, (296.0, yb, 392.0, yt), f'enviar_{idx}', 'Comprobar y enviar',
           'Comprueba que no falte nada y envía la solicitud por correo', GREEN, js_action('maEnviar();'))
    button(page, (398.0, yb, 474.0, yt), f'imprimir_{idx}', 'Imprimir', 'Imprimir el formulario', BLUEB,
           js_action('this.print({bUI: true, bShrinkToFit: true});'))
    button(page, (480.0, yb, 560.0, yt), f'borrar_todo_{idx}', 'Borrar todo', 'Borrar todos los datos del formulario', RED,
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

w.add_metadata({'/Title': 'medassure beauty – Información económica y solicitud', '/Author': 'IberAssekuranz Brokers'})
with open(out, 'wb') as f:
    w.write(f)
r = PdfReader(out); print('fields:', len(r.get_fields()))
