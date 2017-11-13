import unittest
from gedcom_parser import parse

class US16(unittest.TestCase):

    def test_fail_on_different_last_names(self):
        people, families, errors, lists = parse('gedcom/differentsonname.ged')
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()
