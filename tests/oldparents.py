import unittest
from gedcom_parser import parse

class OldParents(unittest.TestCase):

    def test_old_dad(self):
        people, families, errors, lists = parse('gedcom/olddad.ged')
        self.assertEqual(len(errors), 1)

if __name__ == '__main__':
    unittest.main()
