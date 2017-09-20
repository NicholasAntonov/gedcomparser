import unittest
from parser import parse

class ErrorOnFutureDates(unittest.TestCase):

    def test_no_fail_on_past_dates(self):
        people, families, errors = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
