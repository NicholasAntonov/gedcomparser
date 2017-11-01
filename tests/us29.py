import unittest
from pathlib import Path
from gedcom_parser import parse


class us29(unittest.TestCase):
    def testdead(self):
    	people, families, errors, lists = parse('2alive1dead.ged')
    	my_file = Path("../deadpeople.txt/..")
    	if my_file.is_file():
    		self.assertEqual()

if __name__ == '__main__':
    unittest.main()
