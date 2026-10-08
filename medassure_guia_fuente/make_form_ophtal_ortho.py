"""Fillable versions of the medassure ophtal and medassure ortho forms (same features as dental and adipo).

Usage: python3 make_form_ophtal_ortho.py ophtal originales/Formulario_-_Medassure_Ophtal.pdf originales/layout_ophtal.json \
           ../medassure_ophtal_Formulario_rellenable.pdf
       python3 make_form_ophtal_ortho.py ortho  originales/Formulario_-_Medassure_Ortho.pdf  originales/layout_ortho.json \
           ../medassure_ortho_Formulario_rellenable.pdf
       (add --debug to outline every field in red, to check that it sits on the printed form)

The base PDF and the layout (position of every field, in points from the top-left corner of its page) come from
make_original_ophtal_ortho.js. Prices are the ones in the flyers (originales/Flyer_-_Medassure_*.pdf).
"""
import json
import sys
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (NameObject, DictionaryObject, TextStringObject, ArrayObject, FloatObject,
                           NumberObject, StreamObject)

args = [a for a in sys.argv[1:] if a != '--debug']
DEBUG = '--debug' in sys.argv
product, src, layout_path, out = args
assert product in ('ophtal', 'ortho')
orig = PdfReader(src)
LAY = json.load(open(layout_path))
W, H = [float(v) for v in orig.pages[0].mediabox[2:]]
T = colors.Color(1, 1, 1, alpha=0)
INK = colors.Color(0.05, 0.15, 0.35)

# ---- tariff data from the flyers: B = Básica, P = Premium; ophtal: [1, 2, 5 years], ortho: 1 year ----
PRICES = {'ophtal': {'B': [99, 168, 375], 'P': [169, 258, 525]},
          'ortho': {'B': 599, 'P': 899}}[product]
TIPOS = {'ophtal': [('lasik', 'LASIK'), ('lasek', 'LASEK'), ('prk', 'PRK'), ('smile', 'SMILE'),
                    ('cataratas', 'Cirugía de cataratas')],
         'ortho': [('rodilla', 'Prótesis de rodilla'), ('cadera', 'Prótesis de cadera')]}[product]
MEDICO = {'ophtal': ('oftalmologo_clinica', 'Oftalmólogo/a y clínica'),
          'ortho': ('cirujano_clinica', 'Cirujano/a y clínica')}[product]

ov = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
c = canvas.Canvas(ov, pagesize=(W, H))
FIELDS = [[], []]  # per page: callables that draw the fields (reportlab needs them page by page)
GROUPS = {}


def pos(name):
    p = LAY[name]
    return p['page'], p['x'], p['top'], p['w'], p['h']


def at(name):
    def deco(fn):
        FIELDS[LAY[name]['page']].append(fn)
        return fn
    return deco


def text(name, tip, x, top, w, h, size=9.5, **kw):
    if DEBUG:
        c.setStrokeColor(colors.red); c.setLineWidth(0.4); c.rect(x, H - top - h, w, h, stroke=1, fill=0)
    c.acroForm.textfield(name=name, tooltip=tip, x=x, y=H - top - h, width=w, height=h, fontName='Helvetica',
                         fontSize=size, borderWidth=0, borderColor=T, fillColor=T,
                         textColor=kw.pop('textColor', INK), forceBorder=False, **kw)


def check(name, tip, inset=0.0):
    _, x, top, w, h = pos(name)
    x, top, s = x + inset, top + inset, min(w, h) - 2 * inset
    if DEBUG:
        c.setStrokeColor(colors.red); c.setLineWidth(0.4); c.rect(x, H - top - s, s, s, stroke=1, fill=0)
    c.acroForm.checkbox(name=name, tooltip=tip, x=x, y=H - top - s, size=s, buttonStyle='cross', shape='square',
                        borderWidth=0, borderColor=T, fillColor=T, textColor=INK, forceBorder=False, checked=False)


def radio(group, name, tip, inset=0.0):
    # independent tick box (toggles on/off in every viewer); siblings un-tick each other via JS in Acrobat
    GROUPS.setdefault(group, []).append(name)
    FIELDS[LAY[name]['page']].append(lambda: check(name, tip, inset))


def line_field(name, tip, h=10.5, size=9.5):
    # text sits on the printed underline (the bottom edge of the layout box)
    def draw():
        _, x, top, w, hh = pos(name)
        text(name, tip, x + 1, top + hh - h - 0.5, w - 2, h, size=size)
    FIELDS[LAY[name]['page']].append(draw)


def sign_field(name, tip):
    # page 1: the layout box starts at the signature line; the field goes just above it
    def draw():
        _, x, top, w, _ = pos(name)
        text(name, tip, x + 1, top - 21.5, w - 2, 21, size=11)
    FIELDS[LAY[name]['page']].append(draw)


# ---------- page 1 ----------
radio('decision', 'decision_contratar', 'Deseo contratar el seguro', 1)
radio('decision', 'decision_renunciar', 'Renuncio al seguro', 1)
sign_field('p1_lugar_fecha', 'Lugar y fecha')
sign_field('p1_firma', 'Firma del/de la paciente')

# ---------- page 2 ----------
for name, tip in [('apellidos_nombre', 'Apellidos, nombre'), ('fecha_nacimiento', 'Fecha de nacimiento (DD/MM/AAAA)'),
                  ('calle_numero', 'Calle, número'), ('cp_localidad', 'Código postal y localidad'),
                  ('telefono', 'Teléfono'), ('email', 'E-mail'), MEDICO,
                  ('fecha_intervencion', 'Fecha de la intervención (DD/MM/AAAA)'),
                  ('titular_cuenta', 'Titular de la cuenta'),
                  ('direccion_titular', 'Calle, número / CP y localidad del titular'),
                  ('p2_lugar_fecha', 'Lugar, fecha'), ('p2_firma', 'Firma del tomador y titular de la cuenta')]:
    line_field(name, tip)
for k, tip in TIPOS:
    radio('intervencion', 'intervencion_' + k, 'Tipo de intervención: ' + tip)
radio('tarifa', 'tarifa_basica', 'Tarifa Básica', 1)
radio('tarifa', 'tarifa_premium', 'Tarifa Premium', 1)
if product == 'ophtal':
    for k, tip in [('1_ano', '1 año'), ('2_anos', '2 años'), ('5_anos', '5 años')]:
        radio('duracion', 'duracion_' + k, 'Duración: ' + tip, 1)


@at('iban')
def iban():
    # one continuous comb field (22 digits after "ES") over the printed 22-cell grid
    _, x, top, w, h = pos('iban')
    text('iban', 'IBAN: escriba los 22 dígitos seguidos (sin ES ni espacios)', x + 0.75, top + 0.75, w - 1.5, h - 1.5,
         size=12, maxlen=22, fieldFlags='comb')


@at('prima_total')
def prima():
    _, x, top, w, h = pos('prima_total')
    text('prima_total', 'Prima total (se calcula automáticamente en Adobe Acrobat Reader)', x, top + 2.5, w - 8, h - 5,
         size=12.5, textColor=colors.white)


for page_fields in FIELDS:
    for fn in page_fields:
        fn()
    c.showPage()
c.save()

w = PdfWriter(clone_from=ov)
for i, page in enumerate(w.pages):
    page.merge_page(orig.pages[i], over=False)  # printed form underneath the fields
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
    if name == 'prima_total':
        a[NameObject('/Q')] = NumberObject(2)
        a[NameObject('/Ff')] = NumberObject(1)
        a[NameObject('/AA')] = DictionaryObject({NameObject('/C'): js_action('event.value = maCalc();')})
co = [ref for _, ref, _, fld in widgets() if str(fld.get('/T')) == 'prima_total']
w._root_object['/AcroForm'][NameObject('/CO')] = ArrayObject(co)

# ---- document-level JavaScript (Acrobat / Acrobat Reader) ----
JS = r'''
var maDoc = this;
var MA_PRICES = %(prices)s;
var MA_TIPOS = %(tipos)s;
var MA_REQ = [
  ["apellidos_nombre", "Apellidos, nombre"], ["fecha_nacimiento", "Fecha de nacimiento"],
  ["calle_numero", "Calle, número"], ["cp_localidad", "Código postal y localidad"],
  ["telefono", "Teléfono"], ["email", "E-mail"], ["%(medico)s", "%(medico_tip)s"],
  ["fecha_intervencion", "Fecha de la intervención"],
  ["titular_cuenta", "Titular de la cuenta"], ["direccion_titular", "Dirección del titular de la cuenta"],
  ["p2_lugar_fecha", "Lugar y fecha (página 2)"], ["p1_lugar_fecha", "Lugar y fecha (página 1)"]
];
var MA_DUR = %(dur)s;  // ophtal: 1, 2 or 5 years; ortho: always 1 year
function maF(n) { return maDoc.getField(n); }
function maVal(n) { var f = maF(n); return f ? String(f.valueAsString).replace(/^\s+|\s+$/g, "") : ""; }
function maOn(n) { var f = maF(n); return f ? f.value != "Off" : false; }
function maAny(names) { for (var i = 0; i < names.length; i++) if (maOn(names[i])) return true; return false; }
function maEuro(v) {
  var s = v.toFixed(2).split("."), i = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return i + "," + s[1] + " €";
}
function maTar() { return maOn("tarifa_basica") ? "B" : (maOn("tarifa_premium") ? "P" : ""); }
function maDur() { return maOn("duracion_1_ano") ? 0 : (maOn("duracion_2_anos") ? 1 : (maOn("duracion_5_anos") ? 2 : -1)); }
function maCalc() {
  var tar = maTar();
  if (!tar) return "elija tarifa";
  if (!MA_DUR) return maEuro(MA_PRICES[tar]);
  var d = maDur();
  if (d < 0) return "elija duración";
  return maEuro(MA_PRICES[tar][d]);
}
function maEnviar() {
  if (maOn("decision_renunciar")) {
    app.alert("Ha marcado que renuncia al seguro de complicaciones.\n\nNo es necesario enviar la solicitud: basta con firmar la primera página y entregarla en la clínica.", 3);
    return;
  }
  var miss = [];
  if (!maOn("decision_contratar")) miss.push("Su decisión (página 1)");
  for (var i = 0; i < MA_REQ.length; i++) if (maVal(MA_REQ[i][0]) == "") miss.push(MA_REQ[i][1]);
  if (!maAny(MA_TIPOS)) miss.push("Tipo de intervención");
  if (!maAny(["tarifa_basica", "tarifa_premium"])) miss.push("Selección de tarifa");
  if (MA_DUR && maDur() < 0) miss.push("Duración (1, 2 o 5 años)");
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
      cMsg: "Adjunto la solicitud del seguro de complicaciones medassure %(product)s.\n\nFecha de la intervención: " + maVal("fecha_intervencion") });
  }
}
''' % {'prices': json.dumps(PRICES), 'tipos': json.dumps(['intervencion_' + k for k, _ in TIPOS]),
       'medico': MEDICO[0], 'medico_tip': MEDICO[1], 'dur': 'true' if product == 'ophtal' else 'false',
       'product': product}
w.add_js(JS)


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
    _, x, top, bw, bh = pos(f'botones_{idx}')
    right, yt = x + bw, H - top
    yb = yt - bh
    button(page, (right - 222.0, yb, right - 126.0, yt), f'enviar_{idx}', 'Comprobar y enviar',
           'Comprueba que no falte nada y envía la solicitud por correo', GREEN, js_action('maEnviar();'))
    button(page, (right - 120.0, yb, right - 60.0, yt), f'imprimir_{idx}', 'Imprimir', 'Imprimir el formulario', BLUEB,
           js_action('this.print({bUI: true, bShrinkToFit: true});'))
    button(page, (right - 54.0, yb, right, yt), f'borrar_todo_{idx}', 'Borrar todo', 'Borrar todos los datos del formulario',
           RED, DictionaryObject({NameObject('/S'): NameObject('/ResetForm')}))

# ---- tab order: top-to-bottom, left-to-right; buttons last ----
for page in w.pages:
    annots = [r for r in page['/Annots']]
    def key(r):
        a = r.get_object(); x0, y0, x1, y1 = [float(v) for v in a['/Rect']]
        is_btn = int(a.get('/Ff', 0)) & (1 << 16)
        return (1 if is_btn else 0, round(-y1 / 6), x0)
    page[NameObject('/Annots')] = ArrayObject(sorted(annots, key=key))
    page[NameObject('/Tabs')] = NameObject('/R')

title = {'ophtal': 'medassure ophtal – Información económica y solicitud',
         'ortho': 'medassure ortho – Información económica y solicitud'}[product]
w.add_metadata({'/Title': title, '/Author': 'IberAssekuranz Brokers'})
with open(out, 'wb') as f:
    w.write(f)
r = PdfReader(out); print(out, 'fields:', len(r.get_fields()))
