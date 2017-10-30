import unittest
from gedcom_parser import parse

class Marriagetodescendants(unittest.TestCase):

    def test_fail_on_non_unique(self):
        people, families, errors = parse('gedcom/marriedtograndpa.ged')
        self.assertEqual(len(errors), 2)

    def test_success(self):
        people, families, errors = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
