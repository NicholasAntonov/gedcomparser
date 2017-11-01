import unittest
from pathlib import Path
from gedcom_parser import parse


class us30(unittest.TestCase):
    def testmarriedliving(self):
    	people, families, errors, lists = parse('sample.ged')
    	my_file = Path("../marriedlivingpeople.txt/..")
    	if my_file.is_file():
    		self.assertEqual()

if __name__ == '__main__':
    unittest.main()
