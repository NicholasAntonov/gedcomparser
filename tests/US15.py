import unittest
from gedcom_parser import parse

class US15(unittest.TestCase):

    def test_no_fail_on_lttle_siblings(self):
        people, families, errors, lists = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_on_16_siblings(self):
        people, families, errors, lists = parse('manysiblings.ged')
        self.assertEqual(len(errors), 19)

    def test_fail_finds_id(self):
        people, families, errors, lists = parse('manysiblings.ged')
        self.assertEqual(errors[2].offenders[0], '@F1@')


if __name__ == '__main__':
    unittest.main()
