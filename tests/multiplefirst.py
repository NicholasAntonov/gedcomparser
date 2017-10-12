import unittest
from gedcom_parser import parse

class ErrorOnMultipleFirstNames(unittest.TestCase):
    def test_fail_multiplefirst(self):
        people, families, errors = parse('multiplefirst.ged')
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()
