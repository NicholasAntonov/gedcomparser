import unittest
from gedcom_parser import parse

class nobigamy(unittest.TestCase):

    def test_success(self):
        people, families, errors, lists = parse('us10.ged')
        self.assertEqual(len(errors), 7)

if __name__ == '__main__':
    unittest.main()
