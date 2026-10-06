import sys
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

from tarifa_form import TREATMENTS, DOC_JS  # tariff data from the medassurance.de calculator

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

# ---- document-level JavaScript (Acrobat / Acrobat Reader): see tarifa_form.py ----
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
