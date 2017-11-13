import unittest
from gedcom_parser import parse

class kids5onsameday(unittest.TestCase):

    def test_fail_greater5kids(self):
        people, families, errors, lists = parse('6kidsonsameday.ged')
        self.assertEqual(len(errors), 6)


if __name__ == '__main__':
    unittest.main()
