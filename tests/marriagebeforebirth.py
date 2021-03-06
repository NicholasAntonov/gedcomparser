import unittest
from gedcom_parser import parse

class MarriageBeforeBirth(unittest.TestCase):

    def test_fail_on_marriage_before_birth(self):
        people, families, errors, lists = parse('gedcom/marryinwomb.ged')
        self.assertEqual(len(errors), 4)

if __name__ == '__main__':
    unittest.main()
