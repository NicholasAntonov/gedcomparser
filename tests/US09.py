import unittest
from gedcom_parser import parse

class US09(unittest.TestCase):

    def test_no_fail_on_okay(self):
        people, families, errors = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_on_mother_death(self):
        people, families, errors = parse('motherdeath.ged')
        self.assertEqual(len(errors), 1)
        
    def test_fail_on_father_death(self):
        people, families, errors = parse('fatherdeath.ged')
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()

