import unittest
from gedcom_parser import parse

class US04(unittest.TestCase):
    
    def test_fail_on_incorrect_dates(self):
        people, families, errors, lists = parse('us04.ged')
        self.assertEqual(len(errors), 2)



if __name__ == '__main__':
    unittest.main()

