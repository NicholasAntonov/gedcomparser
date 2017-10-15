import unittest
from gedcom_parser import parse

class US20(unittest.TestCase):

    def test_no_fail_on_legal_marriage(self):
        people, families, errors = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_on_nibling_marriage(self):
        people, families, errors = parse('alabama.ged')
        self.assertEqual(len(errors), 2)

    def test_fail_finds_id(self):
        people, families, errors = parse('alabama.ged')
        self.assertEqual(errors[0].offenders[0], '@I3@')


if __name__ == '__main__':
    unittest.main()
