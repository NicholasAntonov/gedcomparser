import unittest
from parser import parse

class kids5onsameday(unittest.TestCase):

    def test_no_fail(self):
        people, families, errors = parse('sample.ged')
        self.assertEqual(len(errors), 0)

    def test_fail_greater5kids(self):
        people, families, errors = parse('6kidsonsameday.ged')
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()
