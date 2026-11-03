import csv
import io
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from md_table_csv import split_row, tables_from_markdown, csv_text


class TableTests(unittest.TestCase):
    def test_real_example(self):
        tables = tables_from_markdown((ROOT / "examples/table-sample.md").read_text(encoding="utf-8"))
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0][1], ["España", "1.234,50", "audited | draft"])
        self.assertEqual(tables[0][2][-1], "`A|B`")
        self.assertEqual(tables[1][-1], ["Closing", "103"])

    def test_pipes_and_code(self):
        self.assertEqual(split_row(r"| a\|b | `x|y` | ``a`|b`` |"), ["a|b", "`x|y`", "``a`|b``"])
        self.assertEqual(split_row(r"a | b\|"), ["a", "b|"])
        self.assertEqual(split_row(r"a | b\\| c"), ["a", r"b\\", "c"])

    def test_csv_round_trip_and_preservation(self):
        rows = [["Country", "Value"], ["España", "1.234,50"], ['A "quote"', "-20"], ["=1+1", "@text"]]
        text = csv_text(rows)
        self.assertEqual(list(csv.reader(io.StringIO(text))), rows)
        safe = list(csv.reader(io.StringIO(csv_text(rows, spreadsheet_safe=True))))
        self.assertEqual(safe[2][1], "'-20")
        self.assertEqual(safe[3][0], "'=1+1")

    def test_fenced_tables_ignored(self):
        source = "```md\n| A | B |\n| --- | --- |\n| 1 | 2 |\n```\n\n| C | D |\n| --- | --- |\n| 3 | 4 |"
        self.assertEqual(tables_from_markdown(source), [[["C", "D"], ["3", "4"]]])

    def test_plain_text_is_explicit(self):
        self.assertEqual(list(csv.reader(io.StringIO(csv_text([["`A|B`", "[read](https://eqvero.com/)"]], text=True))))[0], ["A|B", "read"])

    def test_ragged_row_rejected(self):
        with self.assertRaises(ValueError):
            tables_from_markdown("| A | B |\n| --- | --- |\n| 1 | 2 | 3 |")


if __name__ == "__main__":
    unittest.main()
