import unittest
from parser import parse

class ErrorOnMultipleFirstNames(unittest.TestCase):

    def test_no_fail_multiplefirst(self):
        people, families, errors = parse('multiplefirst.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_multiplefirst(self):
        people, families, errors = parse('multiplefirst.ged')
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()