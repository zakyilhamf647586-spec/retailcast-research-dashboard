"""Data lineage checks for every frozen derived input in the repository."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FrozenDataIntegrityTest(unittest.TestCase):
    def test_sha256_data_manifest(self):
        manifest = json.loads((ROOT / 'docs' / 'INPUT_SHA256.json').read_text())
        self.assertEqual(len(manifest), 9)
        for name, expected in manifest.items():
            with self.subTest(file=name):
                actual = hashlib.sha256((ROOT / 'data' / name).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)

    def test_no_raw_customer_level_file(self):
        self.assertFalse(any(x.name == 'online_retail_II.xlsx' for x in ROOT.rglob('*')))
        csvs=list((ROOT/'data').glob('*.csv'))
        self.assertEqual(len(csvs),7)
        for file in csvs:
            with file.open(encoding='utf-8') as handle:
                header = handle.readline().casefold()
            self.assertNotIn('customerid',header)
            self.assertNotIn('customer_id',header)

if __name__ == '__main__':
    unittest.main()
