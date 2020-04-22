import unittest
import urwid
import sys
sys.path.insert(0, '../')
import rtv2util as util

class TestRtV2Util(unittest.TestCase):

    def test_dialogcomponents(self):
        dialogComponents = util.DialogComponents()
        dialogComponents.create_form("someTitle", ["someFormField"], urwid.Button("someButton"), urwid.Button("someCancelButton"))

        self.assertEqual('someTitle', dialogComponents.get_title())
        self.assertEqual(["someFormField"], dialogComponents.get_inputs())
        

if __name__ == '__main__':
    unittest.main()
