"""Local, value-preserving pipe-table extraction. No third-party dependencies."""
import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path


def split_row(line):
    """Protect escaped pipes and balanced code spans, including multi-backtick spans."""
    line = line.strip()
    cells, current, index = [], [], 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line):
            # A literal escaped pipe belongs to the value; other escapes remain unchanged.
            following = line[index + 1]
            current.append(following if following == "|" else line[index:index + 2])
            index += 2
            continue
        if char == "`":
            end = index
            while end < len(line) and line[end] == "`":
                end += 1
            marker = line[index:end]
            closing = re.search(r"(?<!`)" + re.escape(marker) + r"(?!`)", line[end:])
            if closing:
                stop = end + closing.end()
                current.append(line[index:stop])
                index = stop
                continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    if line.startswith("|"):
        cells.pop(0)
    # Only remove a trailing outer border if the parser actually saw a separator.
    if line.endswith("|") and cells and cells[-1] == "":
        cells.pop()
    return cells


def tables_from_markdown(source):
    lines = source.splitlines()
    result = []
    index = 0
    fence = None
    while index < len(lines):
        line = lines[index]
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.match(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*$", line):
                fence = None
            index += 1
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            index += 1
            continue
        if index + 1 >= len(lines) or "|" not in line:
            index += 1
            continue
        header = split_row(line)
        delimiter = split_row(lines[index + 1])
        if len(header) < 2 or len(delimiter) != len(header) or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in delimiter):
            index += 1
            continue
        rows = [header]
        index += 2
        while index < len(lines) and "|" in lines[index] and lines[index].strip():
            if re.match(r"^ {0,3}(`{3,}|~{3,})", lines[index]):
                break
            row = split_row(lines[index])
            if len(row) != len(header):
                raise ValueError(f"line {index + 1}: expected {len(header)} cells, got {len(row)}; refusing silent padding/truncation")
            rows.append(row)
            index += 1
        result.append(rows)
    return result


def plain_text(value):
    value = re.sub(r"(`+)(.*?)\1", lambda match: match[2].strip(), value)
    value = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", value)
    return value


def csv_text(rows, text=False, spreadsheet_safe=False):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for row in rows:
        values = [plain_text(cell) if text else cell for cell in row]
        if spreadsheet_safe:
            values = ["'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value for value in values]
        writer.writerow(values)
    return output.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract strict, single-line Markdown pipe tables; keep decimal commas and cell values. No PDF parsing.")
    parser.add_argument("input", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="list table numbers and headers as JSON")
    group.add_argument("--table", type=int, default=None, help="1-based table number (default 1)")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--output", type=Path, help="one CSV file; default stdout")
    parser.add_argument("--output-dir", type=Path, help="required with --all")
    parser.add_argument("--text", action="store_true", help="remove simple inline-code/link markup; HTML stays literal")
    parser.add_argument("--spreadsheet-safe", action="store_true", help="prefix formula-like values with an apostrophe; changes original values, including negative numbers")
    args = parser.parse_args(argv)
    try:
        tables = tables_from_markdown(args.input.read_text(encoding="utf-8-sig"))
        if not tables:
            raise ValueError("no supported pipe tables found")
        if args.list:
            print(json.dumps([{"table": i + 1, "headers": table[0], "rows": len(table) - 1} for i, table in enumerate(tables)], ensure_ascii=False, indent=2))
            return 0
        if args.all:
            if args.output or not args.output_dir:
                raise ValueError("--all requires --output-dir and cannot use --output")
            args.output_dir.mkdir(parents=True, exist_ok=True)
            selected = [(i + 1, table) for i, table in enumerate(tables)]
        else:
            if args.output_dir:
                raise ValueError("--output-dir requires --all")
            number = args.table if args.table is not None else 1
            if number < 1 or number > len(tables):
                raise ValueError(f"table must be in 1..{len(tables)}")
            selected = [(number, tables[number - 1])]
        for number, table in selected:
            content = csv_text(table, args.text, args.spreadsheet_safe)
            destination = args.output_dir / f"table-{number:03d}.csv" if args.all else args.output
            if destination:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(content, encoding="utf-8", newline="")
            else:
                sys.stdout.write(content)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Cannot export: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
