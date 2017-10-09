import unittest
from parser import parse

class ChildrenBeforeMarriage(unittest.TestCase):
    def test_born_before(self):
        people, families, errors = parse('bornbeforemarriage.ged')
        self.assertEqual(len(errors), 3)

    def test_error_element(self):
        people, families, errors = parse('bornbeforemarriage.ged')
        self.assertEqual(errors[0].offenders[0], '@I1@')


if __name__ == '__main__':
    unittest.main()
