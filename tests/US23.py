import unittest
from gedcom_parser import parse

class Uniquenamesandbirthdays(unittest.TestCase):

    def test_fail_on_non_unique(self):
        people, families, errors, lists = parse('gedcom/multiplenamesandbirths.ged')
        self.assertEqual(len(errors), 3)

    def test_success(self):
        people, families, errors, lists = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
