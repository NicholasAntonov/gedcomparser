import unittest
from gedcom_parser import parse

class ErrorSiblingMarriage(unittest.TestCase):

    def test_fail_when_siblings_marry(self):
        people, families, errors, lists = parse('alabama.ged')
        self.assertEqual(len(errors), 6)

    def test_fail_finds_id(self):
        people, families, errors, lists = parse('alabama.ged')
        self.assertEqual(errors[0].offenders[0], '@I3@')
        self.assertEqual(errors[1].offenders[0], '@I4@')

    def test_correct_number_of_offenders(self):
        people, families, errors, lists = parse('alabama.ged')
        self.assertEqual(len(errors[0].offenders), 1)

    def test_correct_severity(self):
        people, families, errors, lists = parse('alabama.ged')
        self.assertEqual(errors[0].severity, 2)

if __name__ == '__main__':
    unittest.main()
