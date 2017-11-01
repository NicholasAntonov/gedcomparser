import unittest
from gedcom_parser import parse

class UniqueIds(unittest.TestCase):
    def test_individuals_are_unique(self):
        people, families, errors, lists = parse('gedcom/sameidpeople.ged')
        self.assertEqual(len(errors), 1)

    def test_ids_checked_between_people_and_families(self):
        people, families, errors, lists = parse('gedcom/sameidasfamily.ged')
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()
