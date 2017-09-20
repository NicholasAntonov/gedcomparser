import unittest
from parser import parse

class ErrorOnFutureDates(unittest.TestCase):

    def test_no_fail_on_past_dates(self):
        people, families, errors = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_on_future_date(self):
        people, families, errors = parse('futurenick.ged')
        self.assertEqual(len(errors), 1)

    def test_fail_finds_id(self):
        people, families, errors = parse('futurenick.ged')
        self.assertEqual(errors[0].offenders[0], '@I1@')

    def test_correct_number_of_offenders(self):
        people, families, errors = parse('futurenick.ged')
        self.assertEqual(len(errors[0].offenders), 1)

    def test_correct_severity(self):
        people, families, errors = parse('futurenick.ged')
        self.assertEqual(errors[0].severity, 1)

if __name__ == '__main__':
    unittest.main()
