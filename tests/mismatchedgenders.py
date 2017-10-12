import unittest
from gedcom_parser import parse

class ErrorOnGenderRoles(unittest.TestCase):
    
    def test_no_fails_when_correct(self):
        people, families, errors = parse('correctgenders.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_when_female_husband(self):
        people, families, errors = parse('ladyhusband.ged')
        self.assertEqual(len(errors), 1)

    def test_fail_when_male_wife(self):
        people, families, errors = parse('dudewife.ged')
        self.assertEqual(len(errors), 1)

    def test_fail_finds_id(self):
        people, families, errors = parse('ladyhusband.ged')
        self.assertEqual(errors[0].offenders, '@F1@')

    def test_correct_severity(self):
        people, families, errors = parse('ladyhusband.ged')
        self.assertEqual(errors[0].severity, 1)

if __name__ == '__main__':
    unittest.main()