import unittest
from pathlib import Path
from gedcom_parser import parse


class us31(unittest.TestCase):
    def testsingleliving(self):
    	people, families, errors = parse('sample.ged')
    	my_file = Path("../singlelivingpeople.txt/..")
    	if my_file.is_file():
    		self.assertEqual()

if __name__ == '__main__':
    unittest.main()