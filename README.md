# Markdown Table to CSV

Extract strict Markdown pipe tables locally, preserving decimal commas and cell strings. Python **3.11+**, standard library only. No PDF parsing, OCR, network, API key or model.

[Español](README.es.md) · [Table Workshop](https://markdown.findfindata.com/)

## Run

```sh
git clone https://github.com/faigvain-ang/md-table-to-csv.git
cd md-table-to-csv
python md_table_csv.py examples/table-sample.md --list
python md_table_csv.py examples/table-sample.md --table 1 --output out/revenue.csv
python md_table_csv.py examples/table-sample.md --all --output-dir out/tables
python -m unittest discover -s tests -v
python site/build.py
```

Use `python3` where appropriate. No installation or third-party dependencies are required; clone and run the file. `--table` is 1-based and defaults to 1. Without `--output`, a selected table is printed to stdout. All exports use UTF-8, comma delimiters and RFC-style CSV quoting; open with UTF-8/comma settings in spreadsheet software.

## Real synthetic example

```markdown
| Country | Revenue | Note |
| :--- | ---: | --- |
| España | 1.234,50 | audited \| draft |
| México | 900,25 | `A|B` |
```

Default output:

```csv
Country,Revenue,Note
España,"1.234,50",audited | draft
México,"900,25",`A|B`
```

`1.234,50` stays one string, not `1234.50` and not two columns. Default mode preserves inline markup and numeric strings; surrounding cell whitespace and the Markdown escape on `\|` are removed. Balanced backtick spans, including multiple-backtick delimiters, protect internal pipes. This is an intentional **pipe-table subset**, not a claim of complete GFM/CommonMark conformance: dialects that require escaping a pipe even inside code may parse the same source differently.

`--text` explicitly removes simple inline-code and link wrappers; it is not a complete Markdown/HTML renderer. HTML is treated as literal text. `--spreadsheet-safe` explicitly prefixes formula-like cells beginning (after whitespace) with `=`, `+`, `-`, `@` with an apostrophe. **This changes values, including negative numbers.** Default export does not add this prefix. CSV quoting alone does not neutralize formulas; do not open untrusted raw exports as executable spreadsheet content. The optional prefix is a precaution, not a guarantee across every spreadsheet application.

## Limits

Single-line cells, two or more columns, delimiter cells of at least three hyphens with optional alignment colons. Fenced code blocks are ignored. No HTML tables, merged/multiline cells, lists/blockquote nesting, type inference, locale conversion or PDF extraction. Ragged body rows fail rather than being silently padded/truncated. Values that are wrong in the source remain wrong. Exit **0** success, **2** invalid input/selection.

## Documentation and PDF workflows

Run `python site/build.py` to generate the bilingual guides in `docs/` from the sources in `site/`.

If your starting file is a PDF, [KolmoPDF PDF to Markdown](https://www.kolmopdf.com/pdf-to-markdown) can provide the upstream conversion. It uploads documents to the cloud; this CLI processes the resulting Markdown locally. Check important table values against the source before using them in calculations.

MIT license. Synthetic examples. No third-party runtime dependencies.
