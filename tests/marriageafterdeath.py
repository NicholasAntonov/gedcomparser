import unittest
from gedcom_parser import parse

class MarriageAfterDeath(unittest.TestCase):

    def test_fail_on_marriage_before_birth(self):
        people, families, errors = parse('gedcom/spookymarriage.ged')
        self.assertEqual(len(errors), 1)

if __name__ == '__main__':
    unittest.main()
