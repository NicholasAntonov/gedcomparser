import unittest
from gedcom_parser import parse

class ErrorOnUS24(unittest.TestCase):
    
    def test_no_fails_when_correct(self):
        people, families, errors, lists = parse('correctgenders.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_when_non_unique_family(self):
        people, families, errors, lists = parse('gedcom/Nonuniquefamily.ged')
        self.assertEqual(len(errors), 2)


if __name__ == '__main__':
    unittest.main()
