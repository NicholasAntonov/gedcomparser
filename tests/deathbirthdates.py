import unittest
from gedcom_parser import parse

class ErrorOnDeathBeforeBirth(unittest.TestCase):

    def test_no_fail_on_normal_death(self):
        people, families, errors = parse('nickdead.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_on_death_before_birth(self):
        people, families, errors = parse('nickdeadbeforebirth.ged')
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()
