import unittest
from gedcom_parser import parse

class RecentlyDead(unittest.TestCase):

    def test_no_old_deaths(self):
        people, families, errors, lists = parse('nickdead.ged')
        self.assertEqual(len(lists['recentlydead']), 0)

    def test_find_recent_death(self):
        people, families, errors, lists = parse('gedcom/nickjustdied.ged')
        self.assertEqual(len(lists['recentlydead']), 1)


if __name__ == '__main__':
    unittest.main()
