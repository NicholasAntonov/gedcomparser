import unittest
from gedcom_parser import parse

class US07(unittest.TestCase):

    def test_no_fail_on_reasonable_age(self):
        people, families, errors = parse('simplegood.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_on_old_person(self):
        people, families, errors = parse('olddude.ged')
        self.assertEqual(len(errors), 1)



if __name__ == '__main__':
    unittest.main()
