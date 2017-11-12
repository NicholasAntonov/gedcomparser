import unittest
from gedcom_parser import parse

class nomultimarry(unittest.TestCase):

    def test_no_fail(self):
        people, families, errors, lists = parse('us11.ged')
        self.assertEqual(len(errors), 8)

if __name__ == '__main__':
    unittest.main()
