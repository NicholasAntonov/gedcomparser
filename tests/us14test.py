import unittest
from gedcom_parser import parse

class kids5onsameday(unittest.TestCase):

    def test_no_fail(self):
        people, families, errors, lists = parse('sample.ged')
        self.assertEqual(len(errors), 2)

    def test_fail_greater5kids(self):
        people, families, errors, lists = parse('6kidsonsameday.ged')
        self.assertNotEqual(len(errors), 0)


if __name__ == '__main__':
    unittest.main()
