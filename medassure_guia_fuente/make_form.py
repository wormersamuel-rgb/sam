import sys
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from pypdf import PdfReader, PdfWriter
src, out = sys.argv[1], sys.argv[2]
orig = PdfReader(src)
W1, H1 = [float(v) for v in orig.pages[0].mediabox[2:]]
W2, H2 = [float(v) for v in orig.pages[1].mediabox[2:]]
T = colors.Color(1,1,1,alpha=0)
INK = colors.Color(0.05,0.15,0.35)
ov = 'overlay.pdf'
c = canvas.Canvas(ov, pagesize=(W1, H1))
af = c.acroForm

def text(name, tip, x, top, w, h, H, size=9.5, **kw):
    af.textfield(name=name, tooltip=tip, x=x, y=H-top-h, width=w, height=h, fontName='Helvetica', fontSize=size,
                 borderWidth=0, borderColor=T, fillColor=T, textColor=INK, forceBorder=False, **kw)
def radio(name, value, tip, x, top, s, H):
    af.radio(name=name, value=value, tooltip=tip, x=x, y=H-top-s, size=s, buttonStyle='circle', shape='circle',
             borderWidth=0, borderColor=T, fillColor=T, textColor=INK, forceBorder=False, selected=False)
def check(name, tip, x, top, s, H):
    af.checkbox(name=name, tooltip=tip, x=x, y=H-top-s, size=s, buttonStyle='cross', shape='square',
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
rows = [(154, 'apellidos_nombre','Apellidos, nombre', 'fecha_nacimiento','Fecha de nacimiento (DD.MM.AAAA)'),
        (173, 'calle_numero','Calle, número', 'cp_localidad','Código postal y localidad'),
        (191, 'telefono','Teléfono', 'email','E-mail'),
        (230, 'cirujano_clinica','Cirujano/a y clínica', 'fecha_operacion','Fecha de la operación (DD.MM.AAAA)'),
        (249, 'tratamiento_1','Tipo de tratamiento 1', 'tratamiento_2','Tipo de tratamiento 2'),
        (268, 'tratamiento_3','Tipo de tratamiento 3', 'tratamiento_4','Tipo de tratamiento 4')]
for top, n1, t1, n2, t2 in rows:
    text(n1, t1, 35, top-11, 248, 10.5, H)
    text(n2, t2, 312, top-11, 248, 10.5, H)
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
text('titular_cuenta', 'Titular de la cuenta', 35, 655, 248, 10.5, H)
text('direccion_titular', 'Calle, número / CP y localidad del titular', 312, 655, 248, 10.5, H)
# IBAN: ES + 2 check digits + 5 groups of 4 (comb fields)
text('iban_control', 'IBAN: 2 dígitos de control', 91.6, 673.4, 33.2, 16.9, H, size=11, maxlen=2, fieldFlags='comb')
for i, x in enumerate([134.3, 209.7, 285.0, 360.3, 435.6]):
    text(f'iban_{i+1}', f'IBAN: bloque {i+1} de 4 dígitos', x, 673.4, 65.8, 16.9, H, size=11, maxlen=4, fieldFlags='comb')
text('p2_lugar_fecha', 'Lugar, fecha', 36, 693, 244, 13.5, H, size=10)
text('p2_firma', 'Firma del tomador y titular de la cuenta', 315, 693, 244, 13.5, H, size=10)
# fix section number 5 -> 4 (sections go 1,2,3,5)
blue = colors.Color(0.16862746, 0.56078436, 0.84705886)
cx, cy, r = 33.7 + 14.1/2, H - (632.9 + 13.5/2), 7.2
c.setFillColor(blue); c.setStrokeColor(blue); c.circle(cx, cy, r, stroke=0, fill=1)
c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 7.5); c.drawCentredString(cx, cy - 2.6, '4')
c.showPage(); c.save()

w = PdfWriter(clone_from=ov)
for i, page in enumerate(w.pages):
    page.merge_page(orig.pages[i], over=False)
w.set_need_appearances_writer(True)
# reportlab offsets the radio dot when borderWidth=0: redraw a centred dot
from pypdf.generic import NameObject
for page in w.pages:
    for ref in page.get('/Annots', []):
        a = ref.get_object()
        par = a.get('/Parent')
        if par is None or par.get_object().get('/FT') != '/Btn' or '/AP' not in a: continue
        if not (int(par.get_object().get('/Ff', 0)) & (1 << 15)): continue  # radios only
        x0, y0, x1, y1 = [float(v) for v in a['/Rect']]
        sz = min(x1 - x0, y1 - y0); c0 = sz / 2; rr = sz * 0.27; k = rr * 0.5523
        path = (f"q .05 .15 .35 rg {c0+rr:.3f} {c0:.3f} m {c0+rr:.3f} {c0+k:.3f} {c0+k:.3f} {c0+rr:.3f} {c0:.3f} {c0+rr:.3f} c "
                f"{c0-k:.3f} {c0+rr:.3f} {c0-rr:.3f} {c0+k:.3f} {c0-rr:.3f} {c0:.3f} c {c0-rr:.3f} {c0-k:.3f} {c0-k:.3f} {c0-rr:.3f} {c0:.3f} {c0-rr:.3f} c "
                f"{c0+k:.3f} {c0-rr:.3f} {c0+rr:.3f} {c0-k:.3f} {c0+rr:.3f} {c0:.3f} c f Q").encode()
        for st, ref2 in a['/AP']['/N'].items():
            if st != '/Off': ref2.get_object().set_data(path)
w.add_metadata({'/Title': 'medassure beauty – Información económica y solicitud', '/Author': 'IberAssekuranz Brokers'})
with open(out, 'wb') as f: w.write(f)
r = PdfReader(out); print('fields:', len(r.get_fields()))
