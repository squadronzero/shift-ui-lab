import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lab  # noqa: E402

PAGE = """<!doctype html><html><head><title>SHIFT fire calendar</title></head>
<body><div id="root"></div></body></html>"""


class Refs(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(lab.parse_refs("main ui/lab-a"), [("main", "main"), ("ui/lab-a", "ui-lab-a")])
        self.assertEqual(lab.parse_refs("main,ui/x"), [("main", "main"), ("ui/x", "ui-x")])

    def test_rejected(self):
        for bad in ["", "a b c d", "main;rm -rf /", "$(id)", "a/../b", "-x", "ui/", "x.lock", "main main",
                    "ui/a ui-a"]:
            with self.assertRaises(ValueError, msg=bad):
                lab.parse_refs(bad)


class Mark(unittest.TestCase):
    def test_mark_once(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d, "index.html")
            f.write_text(PAGE)
            lab.mark(f, "ui/<b>", "abc1234", "https://example.org/")
            t = f.read_text()
            self.assertIn("<title>[Preview] SHIFT", t)
            self.assertIn('name="robots" content="noindex, nofollow"', t)
            self.assertIn("ui/&lt;b&gt;", t)           # escaped
            self.assertNotIn("ui/<b>", t)
            self.assertEqual(t.count('id="lab-flag"'), 1)
            with self.assertRaises(SystemExit):
                lab.mark(f, "x", "y", "z")             # never twice

    def test_index(self):
        with tempfile.TemporaryDirectory() as d:
            lab.index_page(Path(d), "https://example.org/", [("main", "main", "abc"), ("ui/a", "ui-a", "def")])
            t = Path(d, "index.html").read_text()
            self.assertIn('href="./ui-a/"', t)
            self.assertIn("not</strong> the official", t)
            self.assertEqual(Path(d, "robots.txt").read_text(), "User-agent: *\nDisallow: /\n")


if __name__ == "__main__":
    unittest.main()
