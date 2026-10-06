"""Update the treatment dropdowns and premium calculation of an already generated fillable form.

make_form.py needs the original (non-fillable) PDF; this script only swaps the tariff data in the
finished form, so it can be re-run whenever medassure_tarifas/tarifas_medassure_beauty_ES.json changes.

Usage: python3 actualizar_tarifas_formulario.py medassure_beauty_Formulario_rellenable.pdf [out.pdf]
"""
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, NameObject, TextStringObject

from tarifa_form import DOC_JS, TREATMENTS

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else src
w = PdfWriter(clone_from=PdfReader(src))

opts = ArrayObject([TextStringObject(t) for t in [' '] + [t for t, _ in TREATMENTS]])
done = 0
for page in w.pages:
    for ref in page.get('/Annots', []):
        a = ref.get_object()
        if str(a.get('/T', '')).startswith('tratamiento_'):
            a[NameObject('/Opt')] = opts
            a[NameObject('/V')] = a[NameObject('/DV')] = TextStringObject(' ')
            done += 1
assert done == 4, done

names = w._root_object['/Names']['/JavaScript']['/Names']
assert len(names) == 2, 'expected one document-level script'
names[1].get_object()[NameObject('/JS')] = TextStringObject(DOC_JS)

with open(out, 'wb') as f:
    w.write(f)
print(out, '-', done, 'dropdowns,', len(TREATMENTS), 'options')
