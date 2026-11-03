# Markdown Table to CSV

Extrae tablas Markdown de tuberías y conserva las cadenas y comas decimales. **Python 3.11+**, solo biblioteca estándar. Sin PDF, OCR, claves, modelos ni red durante la ejecución.

[English](README.md) · [Table Workshop](https://markdown.findfindata.com/es/)

## Ejecución

```sh
git clone https://github.com/faigvain-ang/md-table-to-csv.git
cd md-table-to-csv
python md_table_csv.py examples/table-sample.md --list
python md_table_csv.py examples/table-sample.md --table 1 --output out/revenue.csv
python md_table_csv.py examples/table-sample.md --all --output-dir out/tables
python -m unittest discover -s tests -v
python site/build.py
```

Use `python3` si corresponde. No necesita instalación, entorno virtual ni dependencias externas. Los índices empiezan en 1; se selecciona la primera tabla por defecto. Sin `--output`, imprime el CSV en la salida estándar. Formato: UTF-8, separador coma, comillas CSV convencionales. Seleccione UTF-8 y coma al importar en una hoja de cálculo.

## Ejemplo sintético

```markdown
| Country | Revenue | Note |
| :--- | ---: | --- |
| España | 1.234,50 | audited \| draft |
| México | 900,25 | `A|B` |
```

Produce:

```csv
Country,Revenue,Note
España,"1.234,50",audited | draft
México,"900,25",`A|B`
```

`1.234,50` sigue siendo una sola cadena. No se convierte a `1234.50` ni se divide en columnas. Por defecto conserva el marcado inline y los números como texto; elimina espacios exteriores de celda y la barra de escape de `\|`. Protege tuberías dentro de fragmentos de código con delimitadores de una o varias comillas invertidas equilibradas. Es un **subconjunto deliberado de tablas**, no una implementación completa de GFM/CommonMark; algunos dialectos exigen escapar las tuberías incluso dentro del código y pueden interpretar el origen de otra manera.

`--text` elimina envolturas simples de código y enlaces; no es un renderizador completo. El HTML permanece literal. `--spreadsheet-safe` añade un apóstrofo a celdas cuyo primer carácter no blanco sea `=`, `+`, `-`, `@`. **Modifica los valores, incluidos negativos**; está desactivado por defecto. Las comillas CSV no impiden ejecutar fórmulas. No abra exportaciones crudas no fiables como contenido ejecutable; el prefijo opcional tampoco garantiza protección en todas las aplicaciones.

## Límites

Celdas de una línea, dos o más columnas, separador de al menos tres guiones por celda con dos puntos opcionales. Ignora bloques de código vallados. No admite tablas HTML, celdas combinadas/multilínea, tablas anidadas en listas/citas, inferencia numérica, conversión regional ni extracción de PDF. Una fila con columnas inconsistentes da error: no rellena ni recorta. Códigos: **0** éxito, **2** entrada o selección inválida.

## Sitio y relación

`site/build.py` genera `docs/` con las fuentes de `site/`. Hostname independiente: `markdown.findfindata.com`. Sin carga de archivos, backend, cuentas ni analítica.

Mantenido por **faigvain-ang**, del mismo equipo que desarrolla herramientas relacionadas con Eqvero, KolmoPDF y KomoPDF. [KolmoPDF PDF a Markdown](https://www.kolmopdf.com/pdf-to-markdown) ofrece la etapa de conversión en la nube: ese servicio carga documentos. Este posprocesador local no lo llama ni contiene su analizador propietario. Licencia MIT; muestras sintéticas; sin dependencias externas.
