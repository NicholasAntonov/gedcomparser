import unittest
from gedcom_parser import parse

class ErrorOnBadDates(unittest.TestCase):

    def test_fail_on_invalid_date(self):
        people, families, errors, lists = parse('gedcom/longfeb.ged')
        self.assertEqual(len(errors), 1)

if __name__ == '__main__':
    unittest.main()
