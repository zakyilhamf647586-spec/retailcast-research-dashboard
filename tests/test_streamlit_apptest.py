"""Real Streamlit AppTest integration; skipped only when Streamlit is unavailable locally.

CI installs Streamlit explicitly, so this test MUST execute there.
"""
import importlib.util
import unittest
from pathlib import Path

HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None

@unittest.skipUnless(HAS_STREAMLIT, "Streamlit not installed in offline environment")
class StreamlitAppTest(unittest.TestCase):
    def test_all_tabs_and_selections(self):
        from streamlit.testing.v1 import AppTest
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        at = AppTest.from_file(str(app_path), default_timeout=90).run()
        self.assertEqual(len(at.exception), 0, [str(e.message) for e in at.exception])
        self.assertEqual(len(at.tabs), 4)
        self.assertGreaterEqual(len(at.selectbox), 3)
        self.assertGreaterEqual(len(at.metric), 10)
        # Re-run for each selectable penalty scenario and the per-SKU filter.
        for label in ("1 : 1", "3 : 1", "5 : 1"):
            at.selectbox[1].set_value(label).run()
            self.assertEqual(len(at.exception), 0, [str(e.message) for e in at.exception])
        first_stockcode = at.selectbox[0].value
        at.selectbox[2].set_value(str(first_stockcode)).run()
        self.assertEqual(len(at.exception), 0, [str(e.message) for e in at.exception])

if __name__ == "__main__":
    unittest.main()
