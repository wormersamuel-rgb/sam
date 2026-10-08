// Formularios base (sin campos) de medassure ophtal y medassure ortho, con el mismo diseño que los de dental y adipo.
// Además del PDF guarda la posición (en puntos, desde la esquina superior izquierda de cada página) de cada
// elemento marcado con data-f, para que make_form_ophtal_ortho.py coloque encima los campos rellenables.
//
// Uso: node make_original_ophtal_ortho.js ophtal originales/Formulario_-_Medassure_Ophtal.pdf originales/layout_ophtal.json
//      node make_original_ophtal_ortho.js ortho  originales/Formulario_-_Medassure_Ortho.pdf  originales/layout_ortho.json
// Versión para imprimir y rellenar a mano (sin recuadro de prima ni layout): añada --imprimir, p. ej.
//      node make_original_ophtal_ortho.js ophtal ../medassure_ophtal_Formulario_imprimir.pdf --imprimir
// Precios y coberturas: folletos «Flyer - Medassure Ophtal» y «Flyer - Medassure Ortho» (originales/).
const fs = require('fs');
const path = require('path');
// DM Sans (SIL OFL, assets/) is the typeface of the medassure logo, as in the dental and adipo forms and the flyers
const font = w => fs.readFileSync(path.join(__dirname, 'assets', `dm-sans-latin-${w}-normal.woff2`)).toString('base64');
const { chromium } = require('playwright');

const IMPRESO = process.argv.includes('--imprimir');  // paper version: blank premium box, instructions for paper
const [product, pdfOut, layoutOut] = process.argv.slice(2).filter(a => a !== '--imprimir');

const P = {
  ophtal: {
    color: '#00A3E0', dark: '#066D96', tint: '#E6F6FC', tintBorder: '#A6DDF2',
    pie: 'Cirugía refractiva ocular y de cataratas',
    aviso: 'AVISO SOBRE LOS COSTES DERIVADOS DE COMPLICACIONES TRAS UNA CIRUGÍA OCULAR',
    marco: `La cirugía refractiva con láser (LASIK, LASEK, PRK, SMILE) que se hace para dejar de depender de gafas o
      lentillas <b>no forma parte, con carácter general, de la cartera de servicios comunes del Sistema Nacional de
      Salud</b>, y la cirugía de cataratas en una clínica privada la paga el propio paciente. Si surge una complicación
      grave, la sanidad pública atenderá al paciente, pero podrá reclamarle después los costes del tratamiento (por
      ejemplo, nuevas intervenciones e ingresos hospitalarios).`,
    privado: `Los seguros de salud privados, por lo general, <b>no cubren las complicaciones derivadas de intervenciones
      oculares que la propia póliza no incluye</b>, como la cirugía refractiva con láser, o solo lo hacen de forma
      limitada. Antes de operarse, le recomendamos consultar con su aseguradora si asumiría esos costes.`,
    extra: 'que cubre también el hospital público si la complicación pone en peligro la vida',
    medico: ['oftalmologo_clinica', 'OFTALMÓLOGO/A Y CLÍNICA'],
    tipos: [['lasik', 'LASIK'], ['lasek', 'LASEK'], ['prk', 'PRK'], ['smile', 'SMILE'], ['cataratas', 'Cirugía de cataratas']],
    implante: 'Implante / lente intraocular', implB: '1.200 €', implP: '1.800 €',
    precios: { B: [99, 168, 375], P: [169, 258, 525] },
    cubre: `Complicaciones fortuitas de la cirugía láser refractiva y de la cirugía de cataratas: honorarios médicos,
      tratamiento ambulatorio o quirúrgico, anestesia, quirófano, estancia en clínica, medicamentos, material y
      laboratorio, UCI en clínica privada y hospital público si la complicación pone en peligro la vida.`,
    importante: `Solo se aseguran intervenciones aún no realizadas. Las prestaciones se pagan según el cuadro de
      indemnización de medassure ophtal.`,
  },
  ortho: {
    color: '#E67E22', dark: '#A0540D', tint: '#FDF1E6', tintBorder: '#F2C9A2',
    pie: 'Prótesis de rodilla y de cadera',
    aviso: 'AVISO SOBRE LOS COSTES DE COMPLICACIONES TRAS UNA PRÓTESIS DE RODILLA O DE CADERA',
    marco: `Cuando una prótesis de rodilla o de cadera se coloca en una clínica privada, <b>la intervención y sus
      posibles complicaciones las paga, con carácter general, el propio paciente</b>. Si surge una complicación grave
      (por ejemplo, una infección o una luxación de la prótesis), la sanidad pública atenderá al paciente, pero podrá
      reclamarle después los costes del tratamiento (por ejemplo, una cirugía de revisión o ingresos hospitalarios).`,
    privado: `Los seguros de salud privados, por lo general, <b>no cubren las complicaciones derivadas de intervenciones
      que la propia póliza no incluye</b>, o solo lo hacen de forma limitada. Antes de operarse, le recomendamos
      consultar con su aseguradora si asumiría esos costes.`,
    extra: 'que cubre también el hospital público si la complicación pone en peligro la vida',
    medico: ['cirujano_clinica', 'CIRUJANO/A Y CLÍNICA'],
    tipos: [['rodilla', 'Prótesis de rodilla'], ['cadera', 'Prótesis de cadera']],
    implante: 'Implante / prótesis articular', implB: '1.500 €', implP: '3.000 €',
    precios: { B: 599, P: 899 },
    cubre: `Complicaciones fortuitas de la prótesis de rodilla o de cadera: honorarios médicos, tratamiento ambulatorio
      o quirúrgico, anestesia, quirófano, estancia en clínica, medicamentos, material y laboratorio, UCI en clínica
      privada y hospital público si la complicación pone en peligro la vida.`,
    importante: `Cobertura exclusiva para prótesis de rodilla y de cadera, y solo para intervenciones aún no realizadas.
      Las prestaciones se pagan según el cuadro de indemnización de medassure ortho.`,
  },
}[product];
if (!P) throw new Error('producto: ophtal u ortho');

const eur = n => n.toLocaleString('de-DE') + ' €';
const contacto = `IberAssekuranz Brokers Correduría de Seguros, S.L.<br>Calle Princesa 25, 2-8 · 28008 Madrid<br>
  Tel. (+34) 672 69 68 21<br><span class="c">medassure@iberassekuranz.es</span>`;
const logo = `<div class="logo"><div class="wm">medassure</div><div class="sub"><i></i><span>${product}</span><i></i></div></div>`;
const footer = n => `<div class="foot"><span class="sq"></span>medassure ${product} &nbsp;·&nbsp; ${P.pie} &nbsp;·&nbsp; España
  <span class="btns" data-f="botones_${n}"></span></div>`;
const field = (name, label, cls = '') => `<div class="fld ${cls}"><div class="lab">${label}</div><div class="ul" data-f="${name}"></div></div>`;
const circ = (name, cls = '') => `<span class="circ ${cls}" data-f="${name}"></span>`;
const sec = (n, t, note = '') => `<div class="sec"><span class="num">${n}</span><h2>${t}</h2>${note ? `<span class="note">${note}</span>` : ''}</div>`;
const cov = (rows) => rows.map(([a, b]) => `<div class="cov"><span>${a}</span><i></i><b>${b}</b></div>`).join('');

let tabla;
if (product === 'ophtal') {
  const d = ['1 AÑO', '2 AÑOS', '5 AÑOS'], k = ['1_ano', '2_anos', '5_anos'];
  tabla = `<table class="pt"><tr><th class="l">DURACIÓN DE LA COBERTURA · PRIMA ÚNICA</th>${d.map((t, i) =>
      `<th>${circ('duracion_' + k[i], 'sm')}${t}</th>`).join('')}</tr>
    <tr><td class="l">Prima única por todo el periodo (IPS incluido)</td>${[0, 1, 2].map(i =>
      `<td>${eur(P.precios.B[i])} / <span class="c">${eur(P.precios.P[i])}</span></td>`).join('')}</tr></table>`;
} else {
  tabla = `<table class="pt"><tr><th class="l">DURACIÓN DE LA COBERTURA</th><th class="w">PRIMA ÚNICA (IPS INCLUIDO)</th></tr>
    <tr><td class="l">1 año</td><td>${eur(P.precios.B)} / <span class="c">${eur(P.precios.P)}</span></td></tr></table>`;
}

const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
@font-face { font-family: 'DM Sans'; font-weight: 700; src: url(data:font/woff2;base64,${font(700)}) format('woff2'); }
@font-face { font-family: 'DM Sans'; font-weight: 500; src: url(data:font/woff2;base64,${font(500)}) format('woff2'); }
body { font-family: Arial, Helvetica, sans-serif; color: #1c2430; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; padding: 11mm 13mm 0; position: relative; overflow: hidden; page-break-after: always; }
.c { color: ${P.color}; }
.head { display: flex; justify-content: space-between; align-items: flex-start; }
.logo { font-family: 'DM Sans', Arial, sans-serif; }
.logo .wm { font-weight: 700; color: ${P.color}; letter-spacing: -0.4px; }
.logo .sub { display: flex; align-items: center; gap: 12px; color: #13202f; font-weight: 500; }
.logo .sub i { flex: 1; height: 1.3px; background: #c8cbcf; }
.p1 .logo { width: 236px; } .p1 .logo .wm { font-size: 49px; line-height: 50px; } .p1 .logo .sub { font-size: 20px; margin-top: 3px; }
.p2 .logo { width: 142px; } .p2 .logo .wm { font-size: 29.5px; line-height: 30px; } .p2 .logo .sub { font-size: 12px; margin-top: 1px; gap: 8px; }
.addr { text-align: right; font-size: 11.5px; line-height: 16px; }
.p2 .addr { font-size: 10.1px; line-height: 14.7px; margin-top: 4px; }
h1 { font-size: 22.7px; margin-top: 40px; }
.kicker { white-space: nowrap; font-size: 9px; letter-spacing: 2.6px; color: #6b7480; font-weight: bold; margin-top: 5px; }
.sec { display: flex; align-items: center; gap: 9px; margin-top: 26px; }
.num { width: 16px; height: 16px; border-radius: 50%; background: ${P.color}; color: #fff; font-size: 9.5px; font-weight: bold;
       display: inline-flex; align-items: center; justify-content: center; }
h2 { font-size: 14.7px; }
.note { font-size: 10.5px; color: #6b7480; margin-left: 4px; }
.p1 .sec { margin-top: 31px; }
.p1 p { font-size: 12.8px; line-height: 19.3px; text-align: justify; margin-top: 9px; }
.dec { display: flex; gap: 14px; align-items: flex-start; border: 1px solid ${P.tintBorder}; background: ${P.tint};
       border-radius: 7px; padding: 15px 16px; margin-top: 17px; font-size: 12.8px; line-height: 14.7px; }
.circ { display: inline-block; width: 18px; height: 18px; border: 1.4px solid #1c2430; border-radius: 50%; flex: none; background: #fff; }
.circ.sm { width: 15px; height: 15px; vertical-align: -3px; margin-right: 5px; }
.box { display: inline-block; width: 15px; height: 15px; border: 1.2px solid #1c2430; flex: none; background: #fff; vertical-align: -3px; }
.confirm { font-weight: bold; font-size: 12.8px; margin-top: 40px; }
.sigs { position: absolute; left: 13mm; right: 13mm; top: 1009px; display: flex; gap: 44px; }
.sigs > div { flex: 1; border-top: 1px solid #1c2430; padding-top: 8px; font-size: 9px; letter-spacing: 2.4px; font-weight: bold; color: #4a5360; }
.foot { position: absolute; left: 13mm; right: 13mm; top: 1076px; border-top: 1px solid #dde1e5; padding-top: 7px;
        font-size: 9px; color: #6b7480; display: flex; align-items: center; }
.foot .sq { width: 9px; height: 9px; background: #9aa3ad; margin-right: 8px; }
.foot .btns { margin-left: auto; width: 296px; height: 21px; }
/* página 2 */
.info { display: flex; gap: 10px; align-items: flex-start; background: ${P.tint}; border: 1px solid ${P.tintBorder}; border-radius: 7px;
        padding: 8px 12px; margin-top: 12px; font-size: 10.7px; line-height: 18.7px; }
.info .i { width: 13px; height: 13px; border-radius: 50%; background: ${P.color}; color: #fff; font-size: 9px; font-weight: bold;
           display: inline-flex; align-items: center; justify-content: center; flex: none; margin-top: 3px; }
.p2 .sec { margin-top: 13px; } .p2 h2 { font-size: 14px; }
.row { display: flex; gap: 42px; }
.fld { flex: 1; margin-top: 6px; }
.lab { font-size: 8.7px; letter-spacing: 1.45px; white-space: nowrap; font-weight: bold; color: #4a5360; }
.ul { height: 19px; border-bottom: 1px solid #1c2430; }
.frame { border: 1px solid #c7ccd2; padding: 10px 13px 12px; margin-top: 12px; }
.opts { display: flex; flex-wrap: wrap; gap: 8px 26px; margin-top: 9px; font-size: 11.2px; }
.opts label { display: inline-flex; align-items: center; gap: 7px; }
.tars { display: flex; gap: 22px; margin-top: 10px; }
.tar { flex: 1; border-radius: 7px; padding: 9px 13px 10px; font-size: 11.2px; line-height: 16px; }
.tar.b { background: #f0f2f4; } .tar.p { background: #FDF3D3; border: 1px solid #F2D27A; }
.tar .t { display: flex; align-items: center; gap: 9px; font-weight: bold; font-size: 13.3px; margin-bottom: 4px; }
.tar.p .t .name { background: #F2D27A; color: #0d1b2a; border-radius: 12px; padding: 3px 12px; }
.tar .pill { margin-left: auto; background: #fff; border: 1px solid ${P.dark}; color: ${P.dark}; border-radius: 9px; font-size: 9.3px; padding: 1px 9px; }
.cov { display: flex; align-items: baseline; gap: 5px; } .cov i { flex: 1; border-bottom: 1px dotted #9aa3ad; }
table.pt { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11.2px; }
.pt th, .pt td { border: 1px solid #c7ccd2; padding: 5px 10px; text-align: center; }
.pt th { font-size: 9px; letter-spacing: 1.8px; }
.pt .l { text-align: left; } .pt th.l { width: 49%; } .pt th.w { width: auto; }
.notes { display: flex; border: 1px solid #c7ccd2; margin-top: 12px; font-size: 10.4px; line-height: 14px; }
.notes > div { flex: 1; padding: 8px 13px; } .notes > div + div { border-left: 1px solid #c7ccd2; }
.iban { display: flex; align-items: center; gap: 12px; margin-top: 12px; font-weight: bold; font-size: 16px; }
.grid { display: flex; height: 29px; width: 572px; border: 1px solid #9aa3ad; }
.grid span { flex: 1; } .grid span + span { border-left: 0.8px solid #9aa3ad; } .grid span.g { border-left: 2px solid #404040; }
.band { display: flex; align-items: center; margin: 10px 0 0 auto; width: 49.4%; height: 29px; background: ${P.dark}; border-radius: 5px;
        color: #fff; font-weight: bold; font-size: 12.5px; padding-left: 13px; }
.band span { flex: 1; height: 100%; margin-left: 12px; }
.impreso .ul { height: 25px; }  /* paper: no premium box, the space goes to taller lines for handwriting */
.impreso .iban { margin-top: 16px; } .impreso .iban + .row .fld { margin-top: 14px; }
.decl { background: #f6f7f8; border: 1px solid #dde1e5; border-radius: 7px; padding: 8px 13px; margin-top: 12px; font-size: 8.5px; line-height: 11px; }
.decl b { font-size: 10.4px; display: block; margin-bottom: 2px; }
</style></head><body>

<div class="page p1${IMPRESO ? ' impreso' : ''}">
  <div class="head">${logo}<div class="addr">${contacto}</div></div>
  <h1>Información económica complementaria</h1>
  <div class="kicker">${P.aviso}</div>
  ${sec(1, 'Marco legal en España')}<p>${P.marco}</p>
  ${sec(2, 'Pacientes con seguro de salud privado')}<p>${P.privado}</p>
  ${sec(3, 'Recomendación: seguro de complicaciones')}
  <p>Para que no tenga que asumir usted esos gastos, le recomendamos contratar un seguro de complicaciones. En nuestra
    clínica puede contratarlo con <b>medassure ${product}</b>, ${P.extra}. Como clínica no obtenemos ninguna ventaja
    económica ni de ningún otro tipo por ofrecérselo.</p>
  ${sec(4, 'Protección de datos')}
  <p>Para poder gestionar el contrato, y conforme al artículo 6.1 b) del RGPD, cederemos sus datos a la compañía
    aseguradora en la medida necesaria para contratar el seguro o tramitar sus prestaciones.</p>
  ${sec(5, 'Su decisión', '(marque la opción elegida)')}
  <div class="dec">${circ('decision_contratar')}<div><b>Deseo contratar el seguro de complicaciones.</b><br>
    El seguro se solicita con el formulario de solicitud. Por favor, <b>rellene todos sus campos</b> y entréguelo junto
    con esta información económica complementaria.</div></div>
  <div class="dec">${circ('decision_renunciar')}<div><b>Renuncio expresamente a contratar el seguro de complicaciones.</b><br>
    Soy consciente de que, si surge una complicación, tendré que asumir yo mismo/a —total o parcialmente— los
    costes de los tratamientos posteriores que sean médicamente necesarios.</div></div>
  <div class="confirm">Confirmo que he leído y comprendido la información anterior.</div>
  <div class="sigs"><div data-f="p1_lugar_fecha">LUGAR Y FECHA</div><div data-f="p1_firma">FIRMA DEL/DE LA PACIENTE</div></div>
  ${footer(1)}
</div>

<div class="page p2${IMPRESO ? ' impreso' : ''}">
  <div class="head">${logo}<div class="addr">${contacto.replace('<br>', ' · ').replace('<br><span', ' · <span')}</div></div>
  <div class="info"><span class="i">i</span><div><b>Cómo funciona:</b> ${IMPRESO
    ? `rellene todos los campos con letra clara, firme y envíe la solicitud (escaneada o en foto) a
    <b>info@medassure.es como máximo 1 día antes de la intervención</b>, o entréguela en la clínica.`
    : `rellene todos los campos y envíe la solicitud a
    <b>info@medassure.es como máximo 1 día antes de la intervención</b>.`} Consultas: <b>+34 672 69 68 21</b>
    (9–18 h; viernes, julio y agosto, 9–15 h).</div></div>
  ${sec(1, 'Datos personales del tomador del seguro')}
  <div class="row">${field('apellidos_nombre', 'APELLIDOS, NOMBRE')}${field('fecha_nacimiento', 'FECHA DE NACIMIENTO (DD/MM/AAAA)')}</div>
  <div class="row">${field('calle_numero', 'CALLE, NÚMERO')}${field('cp_localidad', 'CÓDIGO POSTAL Y LOCALIDAD')}</div>
  <div class="row">${field('telefono', 'TELÉFONO')}${field('email', 'E-MAIL')}</div>
  ${sec(2, 'Datos de la intervención')}
  <div class="row">${field(P.medico[0], P.medico[1])}${field('fecha_intervencion', 'FECHA DE LA INTERVENCIÓN (DD/MM/AAAA)')}</div>
  <div class="frame"><div class="lab">TIPO DE INTERVENCIÓN${product === 'ophtal' ? ' (marque una)' : ' (marque una · cobertura exclusiva para estas dos intervenciones)'}</div>
    <div class="opts">${P.tipos.map(([k, t]) => `<label><span class="box" data-f="intervencion_${k}"></span>${t}</label>`).join('')}</div></div>
  ${sec(3, product === 'ophtal' ? 'Tarifa y duración' : 'Tarifa',
        product === 'ophtal' ? '(marque una tarifa y una duración · en cada casilla: precio Básica / <span class="c">Premium</span>)'
                             : '(marque una tarifa · precio Básica / <span class="c">Premium</span>)')}
  <div class="tars">
    <div class="tar b"><div class="t">${circ('tarifa_basica')}Tarifa Básica</div>
      ${cov([['Prestaciones en clínica privada', 'máx. 7.500 €'], ['Hospital público (Seguridad Social)', 'máx. 100.000 €'], [P.implante, P.implB]])}</div>
    <div class="tar p"><div class="t">${circ('tarifa_premium')}<span class="name">Tarifa Premium</span><span class="pill">COBERTURA AMPLIADA</span></div>
      ${cov([['Prestaciones en clínica privada', 'máx. 15.000 €'], ['Hospital público (Seguridad Social)', 'máx. 150.000 €'], [P.implante, P.implP]])}</div>
  </div>
  ${tabla}
  <div class="notes"><div><b>Qué cubre</b><br>${P.cubre}</div><div><b>¡Importante!</b><br>${P.importante}</div></div>
  ${sec(4, 'Domiciliación SEPA y firma')}
  <div class="row">${field('titular_cuenta', 'TITULAR DE LA CUENTA')}${field('direccion_titular', 'CALLE, NÚMERO / CP Y LOCALIDAD (titular de la cuenta)')}</div>
  <div class="iban">IBAN ES<div class="grid" data-f="iban">${Array.from({ length: 22 }, (_, i) =>
      `<span class="${[2, 6, 10, 14, 18].includes(i) ? 'g' : ''}"></span>`).join('')}</div></div>
  ${IMPRESO ? '' : '<div class="band">PRIMA ÚNICA TOTAL<span data-f="prima_total"></span></div>'}
  <div class="row">${field('p2_lugar_fecha', 'LUGAR, FECHA', 'sig')}${field('p2_firma', 'FIRMA TOMADOR DEL SEGURO Y TITULAR DE LA CUENTA', 'sig')}</div>
  <div class="decl"><b>Declaración, protección de datos y mandato SEPA</b>
    Confirmo que he leído y acepto las condiciones contractuales publicadas en www.medassure.es, incluidas las condiciones generales del seguro de reembolso de gastos
    derivados de complicaciones fortuitas de medassure ${product} y la información precontractual, y renuncio a recibirlas en papel. Declaro que los datos facilitados son
    veraces y completos. El tomador del seguro y el titular de la cuenta autorizan a Jahnke Hoyer &amp; Cie. GmbH a contactar con ellos ante consultas técnicas y a tratar
    electrónicamente los datos facilitados para tramitar la solicitud. El titular de la cuenta autoriza a Jahnke Hoyer &amp; Cie. GmbH a cobrar la prima única mediante adeudo directo
    SEPA en la cuenta indicada; dispone de ocho semanas desde la fecha del cargo para solicitar su devolución. Una vez realizada la intervención, la prima única corresponde
    íntegramente a la aseguradora. La comparativa de coberturas es un resumen; encontrará la información completa en su documentación contractual.</div>
  ${footer(2)}
</div>
</body></html>`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.setContent(html, { waitUntil: 'load' });
  await p.emulateMedia({ media: 'print' });
  const layout = await p.evaluate(() => {
    const out = {}, pages = [...document.querySelectorAll('.page')];
    for (const el of document.querySelectorAll('[data-f]')) {
      const pg = el.closest('.page'), r = el.getBoundingClientRect(), o = pg.getBoundingClientRect();
      const k = 0.75;  // CSS px -> PDF pt
      out[el.dataset.f] = { page: pages.indexOf(pg), x: (r.left - o.left) * k, top: (r.top - o.top) * k, w: r.width * k, h: r.height * k };
    }
    // bottom of the page content, to check nothing overflows into the footer
    out._overflow = pages.map(pg => [...pg.children].some(c => c.getBoundingClientRect().bottom > pg.getBoundingClientRect().bottom + 0.5));
    return out;
  });
  await p.pdf({ path: pdfOut, preferCSSPageSize: true, printBackground: true });
  if (layoutOut) fs.writeFileSync(layoutOut, JSON.stringify(layout, null, 1));
  await b.close();
  console.log(pdfOut, Object.keys(layout).length - 1, 'posiciones; desborda:', layout._overflow);
})();
