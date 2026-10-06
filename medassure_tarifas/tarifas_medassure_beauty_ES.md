# Tarifas medassure beauty (España)

Extraídas de la calculadora de **medassurance.de** (la que incrusta medassure.es) el 2026-10-06. Datos completos en `tarifas_medassure_beauty_ES.json`; para volver a sacarlos: `python3 extraer_tarifas.py`.

## Precio por categoría

Prima única por todo el periodo, impuestos incluidos. Igual para cualquier país de residencia y de tratamiento (ES, DE, FR, IT, AT).

| Categoría | Básica 1 año | Básica 2 años | Básica 5 años | Premium 1 año | Premium 2 años | Premium 5 años |
|---|---:|---:|---:|---:|---:|---:|
| a | 69 € | 99 € | 129 € | 99 € | 129 € | 149 € |
| b | 99 € | 129 € | 159 € | 149 € | 179 € | 199 € |
| c | 169 € | 219 € | 269 € | 249 € | 299 € | 329 € |
| d | 189 € | 239 € | 289 € | 279 € | 349 € | 399 € |
| e | 289 € | 429 € | 599 € | 429 € | 599 € | 799 € |
| f | 159 € | 189 € | 219 € | 209 € | 239 € | 259 € |

La categoría **f** no aparece en la tabla impresa del formulario: es solo la liposucción de 3 intervenciones con lifting por láser o radiofrecuencia.

## Cómo se calcula la prima

- Se toma el precio de la categoría **más cara** de los tratamientos elegidos, según tarifa y duración.
- Se suma un recargo por número de tratamientos: 2 → +50 €, 3 → +75 €, 4 → +100 €. Es el mismo en Básica y Premium y para cualquier duración.
- Básica admite como máximo 3 tratamientos; Premium, 4.
- Duraciones posibles: 1, 2 o 5 años.
- Ejemplo: rinoplastia (c) + aumento mamario con implantes (e), Básica, 1 año = 289 € + 50 € = 339 €.

## Tratamientos y categoría

| Cat. | Tratamiento (web en español) | Observaciones |
|---|---|---|
| a | Blefaroplastia (cirugía de párpados) |  |
| a | Corrección de orejas prominentes |  |
| a | Liposucción (1 intervención durante el periodo de cobertura) | No se combina con las otras liposucciones |
| a | Trasplante capilar |  |
| b | Aspiración de glándulas sudoríparas |  |
| b | Corrección de cicatrices |  |
| b | Lifting de cuello |  |
| b | Lifting facial (frente, cejas, mejillas, labios, línea del mentón) |  |
| b | Lifting facial con grasa autóloga |  |
| b | Lipoaspiración (1 intervención, incluyendo lifting con láser o radiofrecuencia) | No se combina con las otras liposucciones |
| b | Liposucción (hasta 3 intervenciones durante el periodo de cobertura) | No se combina con las otras liposucciones |
| b | Reducción de los labios vaginales |  |
| c | Abdominoplastia |  |
| c | Balón gástrico | No se combina con ningún otro tratamiento |
| c | Cirugía de glúteos: aumento con grasa autóloga |  |
| c | Cirugía de glúteos: lifting |  |
| c | Cirugía de nariz / Rinoplastia |  |
| c | Cirugía de pantorrillas: reducción |  |
| c | Cirugía íntima / Cirugía estética genital |  |
| c | Lifting de brazos |  |
| c | Lifting de muslos |  |
| d | Bodylift 360° (abdomen, flancos/cintura, espalda) |  |
| d | Cirugía de mamas con grasa autóloga |  |
| d | Cirugía mamaria: extracción de implantes |  |
| d | Cirugía mamaria: ginecomastia |  |
| d | Cirugía mamaria: mastectomía |  |
| d | Cirugía mamaria: reducción / lifting |  |
| d | Corrección de los pezones |  |
| e | Cirugía de glúteos: aumento con implantes |  |
| e | Cirugía de mentón con implante |  |
| e | Cirugía de pantorrillas: aumento con implantes |  |
| e | Cirugía mamaria con implantes | No asegurable si hay contractura capsular diagnosticada |
| e | Cirugía mamaria: sustitución de implantes | No asegurable si hay contractura capsular diagnosticada |
| e | Reducción gástrica (Overstitch, POSE, Endomina) |  |
| f | Liposucción (3 intervenciones, incluyendo lifting con láser o radiofrecuencia) | No se combina con las otras liposucciones |

## Liposucción

La web tiene cuatro variantes, cada una con su categoría:

| Variante | Categoría |
|---|---|
| 1 intervención | a |
| 1 intervención con lifting por láser o radiofrecuencia (tensado) | b |
| Hasta 3 intervenciones | b |
| 3 intervenciones con lifting por láser o radiofrecuencia (tensado) | f |

El formulario antiguo sumaba el tensado como recargo (+30 € en a, +60 € en b). Con 3 intervenciones da lo mismo, pero con 1 intervención en **Premium** salía 20 € más barato que en la web (p. ej. 129 € en vez de 149 € a 1 año). Ya está corregido.

## Otros datos de la calculadora

- Edad del asegurado: de 18 a 84 años.
- La web llama a la tarifa básica «Base»; el formulario y la carta la llaman «Básica».
